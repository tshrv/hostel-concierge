import asyncio
import sys

from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger

from agent.settings import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    api_key=settings.google_api_key,
    project=settings.google_cloud_project,
    vertexai=True,
)

ALLOWED_RESEARCH_TOOLS = ["search_docs"]
ALLOWED_DATA_TOOLS = ["calculate_average"]

def select_tools(all_tools, allowed_tools: set[str]):
    available = {t.name: t for t in all_tools}

    missing = allowed_tools - available.keys()
    if missing:
        logger.error(f"MCP tools not found: {missing}")
        raise ValueError(f"MCP tools not found: {missing}")

    return [available[name] for name in allowed_tools]

async def main(guest_id: str):
    logger.info(f"Starting orchestrator for guest_id: {guest_id}")
    
    async with MCPAdapter("http://localhost:8000/mcp") as mcp:
        all_tools = await mcp.list_tools()
        research_tools = select_tools(all_tools, ALLOWED_RESEARCH_TOOLS)
        data_tools = select_tools(all_tools, ALLOWED_DATA_TOOLS)

        logger.info("Tool selection complete. Creating agents...")
        research_agent = create_agent(
            llm,
            research_tools,
            system_prompt="You are a research specialist. Use your tools to find information.",
        )
        data_agent = create_agent(
            llm,
            data_tools,
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

        result = await orchestrator.ainvoke(
            {
                "messages": [
                    ("user", "Find out what LangGraph is, then average 10, 20 and 60.")
                ]
            }
        )
        print(result["messages"][-1].text)


if __name__ == "__main__":
    guest_id = sys.argv[1]
    asyncio.run(main(guest_id))
