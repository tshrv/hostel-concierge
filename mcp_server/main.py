import json

from fastmcp import FastMCP
from loguru import logger

mcp = FastMCP("research")

DATA_DIR = "/data"
RESERVATIONS_DATA = f"{DATA_DIR}/reservations.json"
MENU_DATA = f"{DATA_DIR}/menu.json"
KITCHEN_HOURS_DATA = f"{DATA_DIR}/kitchen_hours.json"


def get_guests_data() -> list[dict]:
    try:
        with open(RESERVATIONS_DATA, "r") as f:
            return json.load(f).get("guests", [])
    except FileNotFoundError:
        logger.error(f"Reservations data file not found at {RESERVATIONS_DATA}")
        return []


# Booking tools
@mcp.tool()
def get_guest_info(guest_id: str) -> str:
    """Get guest information by id"""
    logger.info(f"Fetching guest info for '{guest_id}'")
    guests = get_guests_data()

    guest_records = list(filter(lambda g: g["id"] == guest_id, guests))
    return json.dumps(guest_records) if guest_records else "Guest not found"


@mcp.tool()
def search_docs(query: str) -> str:
    """Search internal documents."""
    return f"Results for '{query}': Dummy response"


@mcp.tool()
def calculate_average(numbers: list[float]) -> float:
    """Return the average of a list of numbers."""
    return sum(numbers) / len(numbers)
