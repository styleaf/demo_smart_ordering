from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
load_dotenv()

def create_llm():
    """按 .env 创建百炼上的对话模型。

    参数:
        无。读取 QWEN_MODEL、MODEL_PROVIDER、DASHSCOPE_BASE_URL、DASHSCOPE_API_KEY。

    返回:
        可交给 create_agent 使用的聊天模型。
    """
    llm = init_chat_model(
        model=os.getenv("QWEN_MODEL"),
        model_provider=os.getenv("MODEL_PROVIDER"),
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
    )
    return llm