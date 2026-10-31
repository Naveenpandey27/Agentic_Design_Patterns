"""
Example 8 — Parallel vs. sequential (runs offline, no API key).

Not every step depends on the previous one. When steps are independent, run them in
parallel and merge the results — much faster than forcing them into a line.

- SEQUENTIAL: step B needs step A's output -> must run in order.
- PARALLEL: three independent analyses of the same text -> fan out, then fan in.

In LangGraph, parallel = multiple edges out of one node. To merge concurrent writes
into one state key you give that key a reducer (here, operator.add on a list).

Run:
    python src/08_parallel_vs_sequential.py
"""
import time
import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END


# ---------- PARALLEL: fan out three analyses, fan in with a reducer ----------
class PState(TypedDict):
    text: str
    # Annotated with a reducer so parallel branches can all append safely.
    findings: Annotated[list, operator.add]


def summarize(state: PState) -> dict:
    time.sleep(0.3)                       # pretend each does real work
    return {"findings": [f"summary: {state['text'][:20]}..."]}


def sentiment(state: PState) -> dict:
    time.sleep(0.3)
    return {"findings": ["sentiment: positive"]}


def keywords(state: PState) -> dict:
    time.sleep(0.3)
    return {"findings": ["keywords: agents, pipeline, state"]}


def combine(state: PState) -> dict:
    print("  [combine] merged findings:")
    for f in state["findings"]:
        print(f"    - {f}")
    return {}


def build_parallel():
    b = StateGraph(PState)
    for name, fn in [("summarize", summarize), ("sentiment", sentiment), ("keywords", keywords)]:
        b.add_node(name, fn)
    b.add_node("combine", combine)
    # fan out: START -> all three at once
    for name in ("summarize", "sentiment", "keywords"):
        b.add_edge(START, name)
        b.add_edge(name, "combine")       # fan in: all three -> combine
    b.add_edge("combine", END)
    return b.compile()


if __name__ == "__main__":
    graph = build_parallel()
    print("\nThree independent analyses, run in PARALLEL:\n")
    t0 = time.time()
    graph.invoke({"text": "Agentic pipelines are powerful", "findings": []})
    print(f"\n  parallel wall-time: {time.time() - t0:.2f}s  (≈0.3s, not 0.9s — they overlapped)")
