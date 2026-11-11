import asyncio
import os
from pathlib import Path

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import HumanInTheLoopMiddleware, SummarizationMiddleware

from agent import llm
from agent import tools

my_llm = llm.create_llm()
my_agent = create_agent(
    model=my_llm,
    tools=[tools.recommend],
    system_prompt="you must call user to check up when you use the @tool-function of recommend",
    middleware=[
        HumanInTheLoopMiddleware(interrupt_on={"recommend":True}),
        SummarizationMiddleware(model=my_llm,trigger={"messages":2})
    ]
)