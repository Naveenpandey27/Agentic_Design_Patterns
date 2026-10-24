"""
Example 5 — A multi-agent router system.

The router picks a lane; a *real* specialist agent (from agents.py) handles it.
Each specialist is a full tool-using agent with only its own tools — the router
is the receptionist deciding which desk you go to.

Run:
    python src/05_multi_agent_router.py
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from router_schemas import RouteDecision, ROUTES
from agents import ask

load_dotenv()

router_llm = init_chat_model("openai:gpt-4o-mini").with_structured_output(RouteDecision)


def route(query: str) -> RouteDecision:
    return router_llm.invoke(
        "You are a router. Pick the best specialist for the query.\n"
        f"Routes: {', '.join(ROUTES)} "
        "(weather=weather/forecasts, math=calculations, general=everything else).\n"
        f"Query: {query}"
    )


def handle(query: str) -> str:
    decision = route(query)
    print(f"  [router] -> {decision.route} (conf {decision.confidence:.2f}): {decision.reasoning}")
    return ask(decision.route, query)   # hand off to the specialist agent


if __name__ == "__main__":
    for q in ["What's the weather in Delhi, and that in Fahrenheit?",
              "What is 18% of 2500?",
              "Give me a one-line history of the internet."]:
        print(f"\nQ: {q}")
        print(f"A: {handle(q)}")
