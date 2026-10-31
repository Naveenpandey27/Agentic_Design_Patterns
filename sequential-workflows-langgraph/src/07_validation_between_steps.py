"""
Example 7 — Validation between steps, with a revise loop (runs offline, no API key).

A sequential pipeline shouldn't blindly pass a bad draft downstream. Add a validation
gate after the draft step: if it fails the quality bar, loop back and revise; if it
passes (or we hit the attempt limit), move on. This is a conditional edge that can
point *backwards* — the key trick.

    START -> draft -> validate --(fail & attempts left)--> draft  (loop)
                               --(pass or out of attempts)--> finalize -> END

Run:
    python src/07_validation_between_steps.py
"""
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

MAX_ATTEMPTS = 3
QUALITY_BAR = 0.8


class State(TypedDict):
    topic: str
    draft: str
    score: float
    attempts: int


def draft_node(state: State) -> dict:
    attempts = state.get("attempts", 0) + 1
    # Simulated: each revision improves quality. (A real node would call the LLM,
    # feeding the previous issues back in to guide the rewrite.)
    draft = f"draft v{attempts} about {state['topic']}"
    print(f"  [draft] produced {draft}")
    return {"draft": draft, "attempts": attempts}


def validate_node(state: State) -> dict:
    # A real validator would use an LLM with structured output (see schemas.QualityCheck).
    score = 0.5 + 0.2 * state["attempts"]
    print(f"  [validate] attempt {state['attempts']} -> score {score:.2f}")
    return {"score": score}


def gate(state: State) -> str:
    """Conditional edge: decide whether to revise again or move on."""
    if state["score"] >= QUALITY_BAR:
        print("  [gate] passed -> finalize")
        return "finalize"
    if state["attempts"] >= MAX_ATTEMPTS:
        print("  [gate] out of attempts -> finalize (best effort)")
        return "finalize"
    print("  [gate] below bar -> revise")
    return "draft"


def finalize_node(state: State) -> dict:
    return {"draft": state["draft"] + f" [final, score={state['score']:.2f}]"}


builder = StateGraph(State)
builder.add_node("draft", draft_node)
builder.add_node("validate", validate_node)
builder.add_node("finalize", finalize_node)

builder.add_edge(START, "draft")
builder.add_edge("draft", "validate")
builder.add_conditional_edges("validate", gate, {"draft": "draft", "finalize": "finalize"})
builder.add_edge("finalize", END)
graph = builder.compile()


if __name__ == "__main__":
    print("\nDraft -> validate -> (revise loop) -> finalize:\n")
    result = graph.invoke({"topic": "validation gates"})
    print("\nRESULT:", result["draft"])
