from fastmcp import FastMCP

mcp = FastMCP("research")

@mcp.tool()
def search_docs(query: str) -> str:
    """Search internal documents."""
    return f"Results for '{query}': LangGraph is a library for stateful agents."

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)  # served at /mcp