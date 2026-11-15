"""
Example 3 — Fan-out / fan-in in LangGraph.

Parallelism in LangGraph = multiple edges out of one point. Here START fans out to
three analysis nodes that run concurrently, then they fan in to a combine node. The
shared 'findings' key uses a reducer so the three concurrent writes merge safely.

    START ─┬─► summarize ─┐
           ├─► sentiment ─┼─► combine ─► END
           └─► keywords  ─┘

Run:
    python src/03_langgraph_parallel.py
"""
import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END

from llm import get_llm

llm = get_llm()


class State(TypedDict):
    text: str
    findings: Annotated[list, operator.add]   # reducer merges concurrent writes


def summarize(state: State) -> dict:
    out = llm.invoke(f"Summarize in one line:\n{state['text']}").content
    return {"findings": [f"summary: {out}"]}


def sentiment(state: State) -> dict:
    out = llm.invoke(f"One word sentiment (positive/negative/neutral):\n{state['text']}").content
    return {"findings": [f"sentiment: {out.strip()}"]}


def keywords(state: State) -> dict:
    out = llm.invoke(f"List 3 keywords, comma-separated:\n{state['text']}").content
    return {"findings": [f"keywords: {out.strip()}"]}


def combine(state: State) -> dict:
    print("Combined findings:")
    for f in state["findings"]:
        print(f"  - {f}")
    return {}


builder = StateGraph(State)
for name, fn in [("summarize", summarize), ("sentiment", sentiment), ("keywords", keywords)]:
    builder.add_node(name, fn)
builder.add_node("combine", combine)
for name in ("summarize", "sentiment", "keywords"):
    builder.add_edge(START, name)      # fan out
    builder.add_edge(name, "combine")  # fan in
builder.add_edge("combine", END)
graph = builder.compile()


if __name__ == "__main__":
    text = "Agentic AI pipelines let small focused agents collaborate on big tasks."
    graph.invoke({"text": text, "findings": []})
