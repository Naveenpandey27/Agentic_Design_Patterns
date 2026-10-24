"""
Example 6 — Confidence-based routing, fallbacks, and ambiguity handling.

A router that acts on a low-confidence guess is worse than one that asks. Here
we use the confidence score from the structured router: above the threshold we
dispatch; below it we fall back to asking the user to clarify instead of guessing.

Run:
    python src/06_confidence_fallback_router.py
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from router_schemas import RouteDecision, ROUTES
from agents import ask

load_dotenv()

CONFIDENCE_THRESHOLD = 0.6

router_llm = init_chat_model("openai:gpt-4o-mini").with_structured_output(RouteDecision)


def route(query: str) -> RouteDecision:
    return router_llm.invoke(
        "Route the query to one specialist and score your confidence honestly. "
        "If the query is vague or could fit several routes, give LOW confidence.\n"
        f"Routes: {', '.join(ROUTES)}.\nQuery: {query}"
    )


def handle(query: str) -> str:
    try:
        decision = route(query)
    except Exception as exc:  # router itself failed -> safe fallback
        return f"[fallback] Routing failed ({exc}); sending to general.\n" + ask("general", query)

    print(f"  [router] -> {decision.route} (conf {decision.confidence:.2f})")

    if decision.confidence < CONFIDENCE_THRESHOLD:
        # Too unsure to commit — ask rather than guess wrong.
        return (f"[clarify] I'm not sure what you need (best guess: {decision.route}, "
                f"confidence {decision.confidence:.2f}). "
                "Could you rephrase — are you asking about weather, a calculation, "
                "or something else?")

    return ask(decision.route, query)


if __name__ == "__main__":
    for q in ["What's the weather in Mumbai?",   # clear -> dispatch
              "Tell me about it",                 # vague -> clarify
              "What is 9 * 9?"]:                  # clear -> dispatch
        print(f"\nQ: {q}")
        print(handle(q))
