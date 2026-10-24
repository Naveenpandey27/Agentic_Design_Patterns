"""
Example 1 — A rule-based router (no LLM).

The simplest possible router: match keywords to decide the lane. Fast, free,
and fully predictable — but brittle, because it only knows the words you listed.
A good baseline to understand what an LLM router buys you.

Run:
    python src/01_rule_based_router.py
"""

WEATHER_WORDS = {"weather", "temperature", "rain", "forecast", "hot", "cold", "humid"}
MATH_WORDS = {"calculate", "sum", "plus", "minus", "times", "divide", "multiply", "%", "average"}


def route(query: str) -> str:
    """Pick a lane by keyword match, defaulting to 'general'."""
    q = query.lower()
    if any(w in q for w in WEATHER_WORDS):
        return "weather"
    if any(w in q for w in MATH_WORDS) or any(c.isdigit() for c in q):
        return "math"
    return "general"


if __name__ == "__main__":
    tests = [
        "What's the weather in Delhi?",
        "Calculate 18% of 2500",
        "Who wrote The Great Gatsby?",
        "Is it going to rain in Mumbai tomorrow?",
    ]
    for q in tests:
        print(f"{route(q):8}  <-  {q}")
