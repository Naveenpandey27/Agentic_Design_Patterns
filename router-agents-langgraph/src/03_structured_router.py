"""
Example 3 — Structured routing with Pydantic.

with_structured_output forces the model to return a RouteDecision object —
a valid route, a confidence score, and its reasoning — instead of free text.
No parsing, no drift, and you get confidence for free (used in example 6).

Run:
    python src/03_structured_router.py
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from router_schemas import RouteDecision, ROUTES

load_dotenv()

# Bind the schema: every call now returns a validated RouteDecision.
router_llm = init_chat_model("openai:gpt-4o-mini").with_structured_output(RouteDecision)

ROUTER_PROMPT = (
    "You are a query router. Decide which specialist should handle the query.\n"
    f"Available routes: {', '.join(ROUTES)}.\n"
    "- weather: anything about weather, temperature, forecasts\n"
    "- math: calculations, arithmetic, numeric problems\n"
    "- general: everything else\n\n"
    "Query: {query}"
)


def route(query: str) -> RouteDecision:
    return router_llm.invoke(ROUTER_PROMPT.format(query=query))


if __name__ == "__main__":
    tests = [
        "What's the temperature in Mumbai?",
        "What is 15% of 2000?",
        "Give me a fun fact about octopuses.",
    ]
    for q in tests:
        d = route(q)
        print(f"{d.route:8} (conf {d.confidence:.2f})  <-  {q}")
        print(f"         reason: {d.reasoning}\n")
