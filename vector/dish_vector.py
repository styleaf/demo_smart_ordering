from FlagEmbedding import BGEM3FlagModel
from pymilvus import MilvusClient

MODEL_PATH = r"C:\Users\Admin\Desktop\BaiduDownload\bge-m3"
MILVUS_URI = "http://localhost:19530"
COLLECTION_NAME = "dish_demo"

# 获得数据库中菜品的信息
def get_dish_information_from_mysql() -> list[str]:
    """从 MySQL 读取上架菜，拼成一段可向量化的文字。

    参数:
        无。连接信息来自 .env。

    返回:
        字符串列表。每道菜一条，内容包含菜名、价格、描述、分类、辣度、口味、食材、做法、是否素食、过敏原。
        查询失败时返回空列表。
    """
    import pymysql
    import os
    from dotenv import load_dotenv
    temp_list = []
    load_dotenv()
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER_NAME"),
        password=os.getenv("MYSQL_USER_PASSWORD"),
        database=os.getenv("MYSQL_DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    cursor = connection.cursor()
    sql = """
        SELECT
        id,
        CONCAT(
            '菜品名称:', dish_name, '\n',
            '价格:', price, '\n',
            '描述:', IFNULL(description, ''), '\n',
            '分类:', category, '\n',
            '辣度:', CASE spice_level
            WHEN 0 THEN '不辣'
            WHEN 1 THEN '微辣'
            WHEN 2 THEN '中辣'
            WHEN 3 THEN '重辣'
            ELSE ''
            END, '\n',
            '口味:', IFNULL(flavor, ''), '\n',
            '主要食材:', IFNULL(main_ingredients, ''), '\n',
            '烹饪方法:', IFNULL(cooking_method, ''), '\n',
            '是否素食:', IF(is_vegetarian = 1, '是', '否'), '\n',
            '过敏原:', IFNULL(allergens, '')
        ) AS text
        FROM menu_items
        WHERE is_available = 1;
    """

    try:
        cursor.execute(sql)
        temp_list = cursor.fetchall()
    except Exception:
        return temp_list
    finally:
        cursor.close()
        connection.close()
    out_list = []
    for every_dict in temp_list:
        out_list.append(every_dict["text"])
    return out_list


def embedding_and_store() -> None:
    """用 bge-m3 把上架菜变成向量，整表写入 Milvus。

    参数:
        无。会先删掉已有的 dish_demo，再新建并插入，避免重复追加。

    返回:
        无。向量维度是 1024。
    """
    milvus_client = MilvusClient(uri=MILVUS_URI)
    if milvus_client.has_collection(COLLECTION_NAME):
        milvus_client.drop_collection(COLLECTION_NAME)
    milvus_client.create_collection(
        dimension=1024,
        collection_name=COLLECTION_NAME,
    )
    embedding_model = BGEM3FlagModel(model_name_or_path=MODEL_PATH)
    sentence_list = get_dish_information_from_mysql()
    vector_list = embedding_model.encode(
        sentences=sentence_list,
        return_dense=True,
    )
    dense_vectors = vector_list["dense_vecs"] #是一个list，里面是numpy数组
    data = []
    index = 0
    while index < len(sentence_list):
        data_dict = {
            "id": index,
            "text": sentence_list[index],
            "vector": dense_vectors[index].tolist(),
        }
        data.append(data_dict)
        index += 1
    milvus_client.insert(data=data, collection_name=COLLECTION_NAME)


def search_similarity(collection_name: str, need_search: str) -> list:
    """把一句话变成向量，在 Milvus 里找出意思最接近的 3 道菜。

    参数:
        collection_name: 集合名，当前使用 dish_demo。
        need_search: 顾客的需求，例如「想吃辣的」。

    返回:
        长度为 3 的字符串列表。每条是写入时拼好的菜品原文。
        总会返回最接近的结果，不表示这句话一定真的对上了某道菜。
    """
    embedding_model = BGEM3FlagModel(model_name_or_path=MODEL_PATH)
    vector = [embedding_model.encode(need_search, return_dense=True)["dense_vecs"].tolist()]
    milvus_client = MilvusClient(uri=MILVUS_URI)
    result = milvus_client.search(
        collection_name=collection_name,
        limit=3,
        data=vector,


        output_fields=["text"],
    )
    out_list = []
    for i in range(3):
        out_list.append(result[0][i]["entity"]["text"])
    return out_list
