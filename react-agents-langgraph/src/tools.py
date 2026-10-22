"""
Shared demo tools used across the examples.

These are deliberately fake/offline so the repo runs without extra API keys
or network access. In a real project the bodies would call a weather API,
hit a database, etc. — but from the model's point of view nothing changes:
it still just reads the docstring and decides when to call them.
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
def c_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return round((celsius * 9 / 5) + 32, 1)


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression, e.g. '3 * (4 + 5)'.
    Supports + - * / ** and parentheses only."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: only numbers and + - * / ( ) are allowed."
    try:
        # eval is locked down to arithmetic by the character check above.
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:  # noqa: BLE001 - surface any error to the model
        return f"Error evaluating expression: {exc}"
