"""
Example 7 — Evaluating router performance.

A router is a classifier, so measure it like one: run a labeled set, compare the
predicted route to the expected route, and report accuracy plus the mistakes.
This is the single most useful habit for shipping a router you can trust.

Run:
    python src/07_evaluate_router.py
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from router_schemas import RouteDecision, ROUTES

load_dotenv()

router_llm = init_chat_model("openai:gpt-4o-mini").with_structured_output(RouteDecision)

# A small labeled test set — (query, expected_route). Grow this over time with
# the real misroutes you see in production.
TEST_SET = [
    ("What's the weather in Delhi?", "weather"),
    ("How humid is it in Mumbai?", "weather"),
    ("Will it rain in Tokyo tomorrow?", "weather"),
    ("What is 15% of 2000?", "math"),
    ("Calculate 12 times 9 minus 7", "math"),
    ("What's the square root of 144?", "math"),
    ("Who wrote Hamlet?", "general"),
    ("Explain gravity in one sentence.", "general"),
    ("What's the capital of Australia?", "general"),
]


def route(query: str) -> str:
    return router_llm.invoke(
        f"Route into one of {ROUTES}. Query: {query}"
    ).route


def evaluate() -> None:
    correct = 0
    misses = []
    for query, expected in TEST_SET:
        predicted = route(query)
        ok = predicted == expected
        correct += ok
        mark = "ok " if ok else "XX "
        print(f"  {mark} expected={expected:8} got={predicted:8}  {query}")
        if not ok:
            misses.append((query, expected, predicted))

    total = len(TEST_SET)
    print(f"\nAccuracy: {correct}/{total} = {correct / total:.0%}")
    if misses:
        print("\nMisroutes to investigate:")
        for q, exp, got in misses:
            print(f"  - '{q}'  expected {exp}, got {got}")


if __name__ == "__main__":
    evaluate()
