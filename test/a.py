from FlagEmbedding import BGEM3FlagModel
from pymilvus import MilvusClient
MODEL_PATH = r"C:\Users\Admin\Desktop\BaiduDownload\bge-m3"
MILVUS_URI = "http://localhost:19530"
#embedding
embed_model = BGEM3FlagModel(
    model_name_or_path=MODEL_PATH
)
#vector_database
milvu_database = MilvusClient(
    uri=MILVUS_URI
)
def store():
    if milvu_database.has_collection("aaa"):
        milvu_database.drop_collection(collection_name="aaa")
    milvu_database.create_collection(
        dimension=1024,
        collection_name="aaa"
    )

    sentences = ["aaa", "bbb", "ccc"]
    res = embed_model.encode(
        return_dense=True,
        sentences=sentences
    )
    vector_list = res["dense_vecs"]
    print(vector_list)
    data = []
    index = 0
    while index < len(vector_list):
        need_dict = {"id": index, "vector": vector_list[index].tolist(), "text": sentences[index]}
        data.append(need_dict)
        index += 1

    milvu_database.insert(
        data=data,
        collection_name="aaa"
    )

def search(user_text:str):
    vector = embed_model.encode(sentences=user_text,return_dense=True)["dense_vecs"].tolist()
    # print(type(vector))
    print(vector)
    res = milvu_database.search(data=[vector],limit=1,collection_name="aaa",output_fields=["text"])
    print(type(res))
    print(res)
    # print(res[0][0]["entity"]["text"])

if __name__ == "__main__":
    # store()
    search("aaa")