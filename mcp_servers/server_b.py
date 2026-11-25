from fastmcp import FastMCP

mcp = FastMCP("data")

@mcp.tool()
def calculate_average(numbers: list[float]) -> float:
    """Return the average of a list of numbers."""
    return sum(numbers) / len(numbers)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8002)