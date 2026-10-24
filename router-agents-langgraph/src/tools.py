"""
Demo tools for the specialist agents.

Fake/offline on purpose so the whole repo runs without extra API keys or
network access. In a real system these would hit a real weather API, a
database, etc. — the routing logic doesn't change either way.
"""
from langchain_core.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    data = {
        "london": "15°C, cloudy",
        "mumbai": "33°C, humid",
        "delhi": "28°C, hazy",
        "tokyo": "19°C, clear",
    }
    return data.get(city.lower(), f"No weather data for '{city}'. Check the spelling.")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '3 * (4 + 5)'.
    Supports + - * / ** and parentheses only."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: only numbers and + - * / ( ) are allowed."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:  # noqa: BLE001
        return f"Error evaluating expression: {exc}"
