import asyncio
import os
from pathlib import Path

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver

from agent import llm
from agent import tools

model = llm.create_llm()
prompt_path = Path(__file__).resolve().parent / "prompt" / "system_prompt.txt"
system_prompt = prompt_path.read_text(encoding="utf-8")

gaode_client = MultiServerMCPClient({
    "amap": {
        "transport": "http",
        "url": "https://mcp.amap.com/mcp?key=" + os.getenv("AMAP_MAPS_API_KEY"),
    }
})
gaode_tools = asyncio.run(gaode_client.get_tools())

restaurant_agent = create_agent(
    model=model,
    tools=[tools.search_is_featured, tools.reservation_tool, tools.recommend,*gaode_tools],
    system_prompt=system_prompt,
    checkpointer=InMemorySaver(),
)

async def chat(user_text: str, thread_id: str) -> str:
    """把顾客的一句话交给餐厅 Agent，返回最终回复。

    参数:
        user_text: 顾客发送的文字。
        thread_id: 会话编号。同一个编号能记住前面的对话。

    返回:
        Agent 最后一条回复的文字。
    """
    memory_config = {"configurable": {"thread_id": thread_id}}
    res_dict = await restaurant_agent.ainvoke(
        {"messages": [{"role": "user", "content": user_text}]},
        config=memory_config,
    )
    return res_dict["messages"][-1].content

async def chat_stream(user_text: str, thread_id: str):
    """边生成边交出餐厅 Agent 的回复。

    参数:
        user_text: 顾客发送的文字。
        thread_id: 会话编号。同一个编号能记住前面的对话。

    返回:
        异步生成器。每次交出一小段给顾客看的文字。
    """
    config = {"configurable": {"thread_id": thread_id}}
    items = restaurant_agent.astream(
        {"messages": [{"role": "user", "content": user_text}]},
        config=config,
        stream_mode="messages",
    )
    async for message, metadata in items:
        if message.content and message.type == "AIMessageChunk":
            yield message.content


if __name__ == "__main__":
    print(asyncio.run(chat("从北京站怎么到餐厅", "gaode_1")))

