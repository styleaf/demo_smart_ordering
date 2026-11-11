import os
from dotenv import load_dotenv
import pymysql
from langchain.tools import tool

@tool(description="按口味、食材、辣度推荐菜时调用")
def recommend(user_text: str) -> list:
    """按顾客的口味描述，从向量库取出最接近的菜。

    参数:
        user_text: 顾客的需求，例如「想吃辣的」。

    返回:
        字符串列表，最多 3 条。每条是一道菜的拼好原文。模型只能看见这个返回值。
    """
    from vector.dish_vector import search_similarity
    recommend_list = search_similarity("dish_demo", user_text)
    return recommend_list

@tool(description="用于顾客询问是否有特色菜时调用")
def search_is_featured() -> list[dict]:
    """查询菜单里标记为招牌的菜。

    参数:
        无。条件是 is_featured = 1。

    返回:
        字典列表。每道菜含 dish_name、price、flavor、category、description。
        查询失败时返回 [{"state": "失败"}]。
    """
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
        SELECT dish_name, price, flavor, category, description
        FROM menu_items
        WHERE is_featured = 1
    """
    try:
        cursor.execute(sql)
        """ 只有删除、提交、修改需要commit"""
        # connection.commit()
        res_list = cursor.fetchall()
    except Exception:
        print("sql error")
        return [{"state":"失败"}]
    finally:
        cursor.close()
        connection.close()
    # print(res_list)
    for dish_dict in res_list:
        dish_dict['price'] = float(dish_dict['price'])
        if dish_dict['description'] is None:
            dish_dict['description'] = ''
    return res_list

from pydantic import BaseModel, Field


class reservation_input_args(BaseModel):
    """预订工具的参数。模型调用 reservation_tool 之前要凑齐这些字段。"""
    num_people: int = Field(description="总客人人数，包含儿童")
    num_children: int = Field(description="其中0到2岁的儿童数量")
    arrival_time: str = Field(description="到达时间，格式为YYYY-MM-DD HH:MM")
    seat_preference: str = Field(description="座位偏好，例如靠窗、包间、大厅")
    main_dish_preference: str = Field(description="主菜偏好")
    other_comments: str = Field(description="其他备注，没有则填无")

@tool(description="用于预定的工具", args_schema=reservation_input_args)
def reservation_tool(
    num_people: int,
    num_children: int,
    arrival_time: str,
    seat_preference: str,
    main_dish_preference: str,
    other_comments: str,
) -> str:
    """确认后写入一条预订。

    参数:
        num_people: 总人数，包含儿童。
        num_children: 其中 0 到 2 岁的儿童数量。
        arrival_time: 到达时间，格式 YYYY-MM-DD HH:MM。
        seat_preference: 座位偏好，例如靠窗、包间、大厅。
        main_dish_preference: 主菜偏好。
        other_comments: 其他备注。没有则填「无」。

    返回:
        成功时返回「预订成功」，失败时返回「预订失败」。
    """
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
        INSERT INTO reservation_order
            (num_people, num_children, arrival_time, seat_preference, main_dish_preference, other_comments)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(
            sql,
            (
                num_people,
                num_children,
                arrival_time,
                seat_preference,
                main_dish_preference,
                other_comments,
            ),
        )
        connection.commit()
    except Exception:
        return "预订失败"
    finally:
        cursor.close()
        connection.close()
    return "预订成功"


if __name__ == "__main__":
    list = search_is_featured()
    print(list)