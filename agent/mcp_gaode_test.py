from langchain.agents import create_agent

import llm
import os
from dotenv import load_dotenv
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

def use_gaode_mcp():
    load_dotenv()
    this_llm = llm.create_llm()
    gaode_key = os.getenv("AMAP_MAPS_API_KEY")
    # url = "https://mcp.amap.com/mcp?key="+gaode_key
    mcp = MultiServerMCPClient({
        "amap": {
            "transport": "http",
            "url": "https://mcp.amap.com/mcp?key=" + gaode_key,
        }
    })
    async def main():
        tools = await mcp.get_tools()
        agent = create_agent(this_llm, tools)
        res = await agent.ainvoke({
            "messages": [{"role": "user", "content": "从我的位置，导航区北京"}]
        })
        print(res["messages"][-1].content)
    asyncio.run(main())

if __name__ == "__main__":
    use_gaode_mcp()