import fastapi
import pymysql
from fastapi import FastAPI
import uvicorn

from test.connect_databases import connect

#practice
""" 查询菜单的接口 """
def create_app():
    """练习用的旧接口，正式入口是 api/main.py。

    参数:
        无。

    返回:
        FastAPI 应用。
    """
    app = FastAPI()
    #practice
    @app.get("/hello")
    def say_hello():
        """练习：返回一段 hello 文字。

        参数:
            无。

        返回:
            字符串 hello。
        """
        return "hello"

    @app.get("/reservation/list")
    def search_reservation():
        """练习：查询预订列表。

        参数:
            无。

        返回:
            预订字典列表。
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
        # [{'num_people': 8, 'num_children': 3, 'arrival_time': datetime.datetime(2026, 10, 3, 18, 30)}]
        for reservation_dict in res_list:
            reservation_dict["arrival_time"] = str(reservation_dict["arrival_time"])
        return res_list

    @app.post("/reservation")
    def add_reservation(num_people:int,num_children:int,arrival_time:str):
        """练习：写入一条预订。

        参数:
            num_people: 总人数。
            num_children: 儿童人数。
            arrival_time: 到达时间。

        返回:
            成功或失败的字典。
        """
        # 链接数据库
        import os
        from dotenv import load_dotenv
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
        flag = 1
        state_list = [{"state":"成功","num_people":num_people,"num_children":num_children,"arrival_time":arrival_time},{"state":"失败"}]
        sql = """
                  INSERT INTO reservation_order (num_people,num_children,arrival_time) VALUES (%s,%s,%s);
              """
        try:
            cursor.execute(sql,(num_people,num_children,arrival_time))
            connection.commit()
            flag = 0
        finally:
            cursor.close()
            connection.close()

        return state_list[flag]


    @app.get("/menu/list")
    def search_menu():
        """练习：查询菜名和价格。

        参数:
            无。

        返回:
            菜品字典列表。
        """
        import pymysql
        from dotenv import load_dotenv
        import os
        #用你已经会的方式连上 menu 库。
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
        #查出每道菜的菜名和价格。
        sql = """
            SELECT dish_name,price from menu_items
        """
        cursor.execute(sql)
        res_list = cursor.fetchall()
        # print(res_tup)
        cursor.close()
        connection.close()
        out_list = []
        #把每一行做成一个字典，价格转成 float (('宫保鸡丁', Decimal('48.00')), ('清炒时蔬', Decimal('28.00')))。
        for dish_dict in res_list:
            price = float(dish_dict['price'])
            dish_dict['price'] = price
            out_list.append(dish_dict)
        #返回这些字典组成的列表。
        return out_list
    return app

if __name__ == "__main__":
    uvicorn.run(create_app(),port=8080)

