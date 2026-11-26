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

ALLOWED_RESERVATIONS_TOOLS = ["get_guest_info"]

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
        reservations_tools = select_tools(all_tools, ALLOWED_RESERVATIONS_TOOLS)

        logger.info("Tool selection complete. Creating agents...")
        reservations_agent = create_agent(
            llm,
            reservations_tools,
            system_prompt="You are a reservations specialist. Use your tools to find information.",
        )

        @tool
        async def ask_reservations(request: str) -> str:
            """Delegate guests and booking related tasks to the reservations specialist."""
            result = await reservations_agent.ainvoke({"messages": [("user", request)]})
            return result["messages"][-1].text

        orchestrator = create_agent(
            llm,
            [
                ask_reservations,
            ],
            system_prompt=(
                "You are an orchestrator. Break the user's request into steps, "
                "delegate each to the right specialist, and combine their answers."
            ),
        )

        result = await orchestrator.ainvoke(
            {
                "messages": [
                    ("user", "Guest G001 is in which room and when is checkout?")
                ]
            }
        )
        print(result["messages"][-1].text)


if __name__ == "__main__":
    guest_id = sys.argv[1]
    asyncio.run(main(guest_id))
