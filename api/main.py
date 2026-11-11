from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

from vector.dish_vector import embedding_and_store


def create_app():
    """创建接口，并在启动时把上架菜重新写入向量库。

    参数:
        无。

    返回:
        配置好路由的 FastAPI 应用。
    """
    app = FastAPI()
    # 启动时加载 Agent。高德工具在这里取出，不能等到请求里再 asyncio.run。
    from agent import chat as chat_module

    embedding_and_store()

    @app.get("/")
    def home_page():
        """打开点餐页面。

        参数:
            无。

        返回:
            ui/index.html。
        """
        page = Path(__file__).resolve().parent.parent / "ui" / "index.html"
        return FileResponse(page)

    @app.get("/faq/suggest")
    def get_user_text_to_faq(user_text: str) -> list:
        """按顾客正在输入的文字，查找固定问答。

        参数:
            user_text: 顾客输入框里的文字。

        返回:
            没匹配到时返回空列表。
            匹配到时返回两项：第 0 项是答案，第 1 项是问题。
        """
        from faq.redis_faq import find_similar_question
        aq_dict = find_similar_question(user_text)
        out_list = []
        if aq_dict["answer"] is None:
            return out_list
        else:
            # list[0]是answer，list[1]是question
            out_list.append(aq_dict["answer"])
            out_list.append(aq_dict["question"])
        return out_list

    @app.get("/reservation/list")
    def search_reservation():
        """查询已有预订的人数、儿童人数和到达时间。

        参数:
            无。

        返回:
            字典列表。arrival_time 已转成字符串，便于接口输出 JSON。
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

    @app.post("/chat")
    async def get_agent_reply(user_text: str, thread_id: str):
        """把顾客的话交给 Agent，返回回复文字。

        参数:
            user_text: 顾客发送的文字。
            thread_id: 会话编号。同一个编号能记住前面的对话。

        返回:
            Agent 最后一条回复。
        """
        return await chat_module.chat(user_text, thread_id)

    @app.post("/chat/stream")
    async def get_agent_reply_by_stream(user_text: str, thread_id: str):
        """边生成边返回 Agent 的回复。

        参数:
            user_text: 顾客发送的文字。
            thread_id: 会话编号。同一个编号能记住前面的对话。

        返回:
            一段段文字组成的流。
        """
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            chat_module.chat_stream(user_text, thread_id),
            media_type="text/plain",
        )


    @app.post("/reservation")
    def add_reservation(num_people: int, num_children: int, arrival_time: str):
        """直接写入一条只含人数和时间的预订。对话预订走 Agent，不走这个接口。

        参数:
            num_people: 总人数。
            num_children: 儿童人数。
            arrival_time: 到达时间。

        返回:
            成功时返回含 state、人数和时间的字典。失败时返回 {"state": "失败"}。
        """
        import os
        from dotenv import load_dotenv
        import pymysql
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
        # flag = 1
        # state_list = [{"state":"成功","num_people":num_people,"num_children":num_children,"arrival_time":arrival_time},{"state":"失败"}]
        sql = """
                  INSERT INTO reservation_order (num_people,num_children,arrival_time) VALUES (%s,%s,%s);
              """
        try:
            cursor.execute(sql,(num_people,num_children,arrival_time))
            connection.commit()
            flag = 0
        except Exception:
            return {"state":"失败"}
        finally:
            cursor.close()
            connection.close()

        return {
            "state": "成功",
            "num_people": num_people,
            "num_children": num_children,
            "arrival_time": arrival_time,
        }


    @app.get("/menu/list")
    def search_menu():
        """查询菜单里每道菜的菜名和价格。

        参数:
            无。

        返回:
            字典列表。每项含 dish_name 和已转成小数的 price。
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