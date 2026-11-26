from fastmcp import FastMCP

mcp = FastMCP("research")

@mcp.tool()
def search_docs(query: str) -> str:
    """Search internal documents."""
    return f"Results for '{query}': Dummy response"

@mcp.tool()
def calculate_average(numbers: list[float]) -> float:
    """Return the average of a list of numbers."""
    return sum(numbers) / len(numbers)
