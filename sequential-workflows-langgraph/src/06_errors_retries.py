"""
Example 6 — Errors, retries, and failures (runs offline, no API key).

In a sequential pipeline one failed step breaks the whole chain, so each step that
can fail (a flaky API, a rate limit) needs a retry with backoff — and a clear give-up
path. This example simulates a flaky step so you can watch the retries without needing
a real unreliable service.

Run:
    python src/06_errors_retries.py
"""
import time
import random
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    topic: str
    draft: str
    error: str


def flaky_call(topic: str) -> str:
    """Pretend this hits an API that fails ~60% of the time."""
    if random.random() < 0.6:
        raise ConnectionError("simulated API timeout")
    return f"draft about {topic}"


def with_retry(fn, *args, max_attempts: int = 4, base_delay: float = 0.2):
    """Retry a callable with exponential backoff; re-raise if it never succeeds."""
    for attempt in range(1, max_attempts + 1):
        try:
            return fn(*args)
        except Exception as exc:  # noqa: BLE001
            wait = base_delay * (2 ** (attempt - 1))
            print(f"    attempt {attempt} failed ({exc}); retrying in {wait:.2f}s")
            if attempt == max_attempts:
                raise
            time.sleep(wait)


def draft_node(state: State) -> dict:
    print("  [draft] calling flaky service...")
    try:
        draft = with_retry(flaky_call, state["topic"])
        print(f"  [draft] success: {draft}")
        return {"draft": draft}
    except Exception as exc:  # the step gave up -> record a safe error, don't crash
        print(f"  [draft] gave up after retries: {exc}")
        return {"error": str(exc), "draft": ""}


def finalize_node(state: State) -> dict:
    if state.get("error"):
        return {"draft": "[fallback] Could not generate a draft; please retry later."}
    return {"draft": state["draft"] + " [finalized]"}


builder = StateGraph(State)
builder.add_node("draft", draft_node)
builder.add_node("finalize", finalize_node)
builder.add_edge(START, "draft")
builder.add_edge("draft", "finalize")
builder.add_edge("finalize", END)
graph = builder.compile()


if __name__ == "__main__":
    random.seed(1)  # deterministic demo
    print("\nRunning a pipeline with a flaky step and retry/backoff:\n")
    result = graph.invoke({"topic": "resilient pipelines"})
    print("\nRESULT:", result["draft"])
