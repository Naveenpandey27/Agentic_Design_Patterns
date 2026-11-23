"""
Example 7 — Aggregating results from multiple workers (runs offline, no API key).

Workers produce scattered pieces; the aggregator (synthesizer) waits for ALL of them
and assembles one result. LangGraph guarantees the aggregator runs only after every
worker finishes, so its state holds every worker's output. This demo uses deterministic
workers and keeps the section ORDER stable even though workers finish in any order.

Run:
    python src/07_aggregation.py
"""
import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class State(TypedDict):
    sections: list
    # workers append (index, text) so the aggregator can restore order
    parts: Annotated[list, operator.add]
    document: str


class WorkerInput(TypedDict):
    index: int
    name: str


def orchestrator(state: State) -> dict:
    sections = ["Introduction", "Details", "Risks", "Conclusion"]
    return {"sections": sections}


def assign(state: State) -> list:
    return [Send("worker", {"index": i, "name": name})
            for i, name in enumerate(state["sections"])]


def worker(payload: WorkerInput) -> dict:
    text = f"(content for {payload['name']})"
    return {"parts": [(payload["index"], f"## {payload['name']}\n{text}")]}


def aggregate(state: State) -> dict:
    """Runs after ALL workers. Sort by index so the document order is deterministic."""
    ordered = [text for _, text in sorted(state["parts"], key=lambda p: p[0])]
    print(f"  aggregating {len(ordered)} sections in stable order")
    return {"document": "\n\n".join(ordered)}


builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("worker", worker)
builder.add_node("aggregate", aggregate)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", assign, ["worker"])
builder.add_edge("worker", "aggregate")
builder.add_edge("aggregate", END)
graph = builder.compile()


if __name__ == "__main__":
    print("\nWorkers finish in any order; aggregator restores section order:\n")
    result = graph.invoke({"parts": []})
    print(result["document"])
