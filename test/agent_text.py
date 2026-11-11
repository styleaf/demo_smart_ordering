"""练习：单独调用一次对话模型。正式创建模型的代码在 agent/llm.py。"""
# from  typing import generator

from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
load_dotenv()

llm = init_chat_model(
    model=os.getenv("QWEN_MODEL"),
    model_provider=os.getenv("MODEL_PROVIDER"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    # timeout=20,
)
# 是一个生成器
def stream_chat(user_text:str,thread_id:str) :
    res = llm.stream()
# print(res.content)