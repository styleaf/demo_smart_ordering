from dotenv import load_dotenv
import os
import pymysql

from agent_text.tools import search_is_featured


def connect():
    """练习：连上 MySQL 并打印当前库的表名。

    参数:
        无。

    返回:
        无。结果打印在终端。
    """

    load_dotenv()
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER_NAME"),
        password=os.getenv("MYSQL_USER_PASSWORD"),
        database=os.getenv("MYSQL_DB_NAME"),
        charset="utf8mb4",
    )


    #创建游标
    cursor = connection.cursor()
    cursor.execute("show tables")
    print(cursor.fetchall())
    cursor.close()
    connection.close()

def connect_menu_items():
    """练习：插入两道菜并打印整张菜单。

    参数:
        无。

    返回:
        无。结果打印在终端。不要重复运行，否则会再插入一遍。
    """
    load_dotenv()
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER_NAME"),
        password=os.getenv("MYSQL_USER_PASSWORD"),
        database=os.getenv("MYSQL_DB_NAME"),
        charset="utf8mb4",
    )
    #create 游标
    cursor = connection.cursor()
    sql = """
        insert into menu_items 
        (dish_name, price, description, category, spice_level, flavor, is_featured) values
        (%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, ("宫保鸡丁", 48, "花生鸡肉", "川菜", 2, "咸鲜微辣", 1))
    cursor.execute(sql, ("清炒时蔬", 28, "当季青菜", "素菜", 0, "清淡", 0))
    connection.commit()

    cursor.execute("select *from menu_items")
    res = cursor.fetchall()
    print(res)
    cursor.close()
    connection.close()
# connect_database()

def connect_reservation_order():
    """练习：查询预订并打印人数与到达时间。

    参数:
        无。

    返回:
        无。结果打印在终端。
    """
    import pymysql
    from dotenv import load_dotenv
    import os
    # 用你已经会的方式连上 menu 库。
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
                SELECT num_people,num_children,arrival_time from reservation_order  
            """
    cursor.execute(sql)
    res_list = cursor.fetchall()
    for reservation_dict in res_list:
        reservation_dict["arrival_time"] = str(reservation_dict["arrival_time"])
    print(res_list)
# connect_reservation_order()

# def func():
#     from agent import tools
#     list = search_is_featured()
#     print(list)
# func()