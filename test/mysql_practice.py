import pymysql
from dotenv import load_dotenv
import os
from dbutils.pooled_db import PooledDB

def pool_test():
    load_dotenv()
    pool = PooledDB(
        creator=pymysql,
        maxconnections=20,
        mincached=2,
        maxcached=5,
        blocking=True,
        ping=1,  # 每次借出时 ping，防止连接失效
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER_NAME"),
        password=os.getenv("MYSQL_USER_PASSWORD"),
        database=os.getenv("MYSQL_DB_NAME"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )
    conn = pool.connection()
    cur = conn.cursor()
    sql = """
        select *from menu_items
    """
    cur.execute(sql)
    res_list = cur.fetchall()
    for res in res_list:
        print(res)


def test():
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
        insert into menu_items (dish_name,price,category) value (%s,%s,%s)
    """
    cursor.execute(sql,("清水白菜","288","素食"))
    connection.commit()
    res = cursor.fetchall()
    cursor.close()
    connection.close()
    print(type(res))
    print(res)

if __name__ == "__main__":
    pool_test()