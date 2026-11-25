import asyncio
import os

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    api_key=os.environ["GOOGLE_API_KEY"],
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    vertexai=True,
)

async def main():
    async with MCPAdapter("http://localhost:8001/mcp") as research_mcp, \
               MCPAdapter("http://localhost:8002/mcp") as data_mcp:

        research_tools = await research_mcp.list_tools()
        data_tools = await data_mcp.list_tools()

        research_agent = create_agent(
            llm, research_tools,
            system_prompt="You are a research specialist. Use your tools to find information.",
        )
        data_agent = create_agent(
            llm, data_tools,
            system_prompt="You are a data analyst. Use your tools for calculations.",
        )

        @tool
        async def ask_researcher(request: str) -> str:
            """Delegate research or information lookup tasks to the research specialist."""
            result = await research_agent.ainvoke({"messages": [("user", request)]})
            return result["messages"][-1].text

        @tool
        async def ask_data_analyst(request: str) -> str:
            """Delegate calculations and data analysis to the data specialist."""
            result = await data_agent.ainvoke({"messages": [("user", request)]})
            return result["messages"][-1].text

        orchestrator = create_agent(
            llm,
            [ask_researcher, ask_data_analyst],
            system_prompt=(
                "You are an orchestrator. Break the user's request into steps, "
                "delegate each to the right specialist, and combine their answers."
            ),
        )

        result = await orchestrator.ainvoke({
            "messages": [("user", "Find out what LangGraph is, then average 10, 20 and 60.")]
        })
        print(result["messages"][-1].text)

asyncio.run(main())