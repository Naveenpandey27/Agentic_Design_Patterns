"""
Example 4 — How state flows between steps (runs offline, no API key).

The star of a sequential workflow is the shared state object. Each node returns a
partial update; LangGraph merges it in and passes the whole thing to the next node.
This example uses deterministic (non-LLM) nodes so you can run it instantly and
watch the state grow step by step.

Run:
    python src/04_state_passing.py
"""
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    topic: str
    outline: str
    draft: str
    final: str
    word_count: int


def plan_node(state: State) -> dict:
    print(f"  [plan ] in : {state}")
    out = {"outline": f"1. intro to {state['topic']}\n2. body\n3. conclusion"}
    print(f"  [plan ] out: {out}\n")
    return out


def draft_node(state: State) -> dict:
    print(f"  [draft] in : outline present = {bool(state.get('outline'))}")
    draft = f"This post covers {state['topic']}. " * 8
    out = {"draft": draft, "word_count": len(draft.split())}
    print(f"  [draft] out: word_count={out['word_count']}\n")
    return out


def edit_node(state: State) -> dict:
    print(f"  [edit ] in : draft has {state['word_count']} words")
    out = {"final": state["draft"].strip() + " [edited]"}
    print(f"  [edit ] out: final ready\n")
    return out


builder = StateGraph(State)
for name, fn in [("plan", plan_node), ("draft", draft_node), ("edit", edit_node)]:
    builder.add_node(name, fn)
builder.add_edge(START, "plan")
builder.add_edge("plan", "draft")
builder.add_edge("draft", "edit")
builder.add_edge("edit", END)
graph = builder.compile()


if __name__ == "__main__":
    print("\nWatch the state object accumulate as it flows through the nodes:\n")
    result = graph.invoke({"topic": "sequential workflows"})
    print("FINAL STATE KEYS:", list(result.keys()))
    print("final:", result["final"][:60], "...")
