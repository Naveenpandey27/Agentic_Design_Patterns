"""
Example 5 — Synchronizing outputs with an aggregation node.

Parallel branches produce many partial results; something has to wait for all of
them and merge them into one answer. That's the aggregation (fan-in) node. It runs
only after every parallel branch has finished, so its state holds all their outputs.

    START ─┬─► angle: technical ─┐
           ├─► angle: business  ─┼─► aggregate ─► END
           └─► angle: risks     ─┘

Run:
    python src/05_aggregation_node.py
"""
import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END

from llm import get_llm

llm = get_llm()

ANGLES = ["technical", "business", "risk"]


class State(TypedDict):
    topic: str
    notes: Annotated[list, operator.add]   # each angle appends its note
    report: str


def make_angle_node(angle: str):
    def node(state: State) -> dict:
        out = llm.invoke(
            f"In 2 sentences, give the {angle} perspective on: {state['topic']}"
        ).content.strip()
        return {"notes": [f"[{angle}] {out}"]}
    return node


def aggregate(state: State) -> dict:
    """Fan-in: runs only after all angle nodes finish; synthesizes one report."""
    joined = "\n".join(state["notes"])
    report = llm.invoke(
        f"Combine these perspectives into one short, coherent paragraph:\n{joined}"
    ).content.strip()
    return {"report": report}


builder = StateGraph(State)
for angle in ANGLES:
    builder.add_node(angle, make_angle_node(angle))
builder.add_node("aggregate", aggregate)
for angle in ANGLES:
    builder.add_edge(START, angle)        # fan out to every angle at once
    builder.add_edge(angle, "aggregate")  # fan in
builder.add_edge("aggregate", END)
graph = builder.compile()


if __name__ == "__main__":
    topic = "adopting multi-agent systems in production"
    print(f"\nTOPIC: {topic}\n")
    result = graph.invoke({"topic": topic, "notes": []})
    print("--- AGGREGATED REPORT ---\n")
    print(result["report"])
