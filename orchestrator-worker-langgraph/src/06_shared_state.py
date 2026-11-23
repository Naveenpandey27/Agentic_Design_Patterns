"""
Example 6 — Managing shared state and worker outputs (runs offline, no API key).

Many workers run at once and all write their results into the same state. Without a
reducer, those concurrent writes conflict. The fix (same as the parallel pattern):
give the shared key a reducer so every worker's output is MERGED, not overwritten.

Run:
    python src/06_shared_state.py
"""
import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class State(TypedDict):
    items: list
    # Each worker returns {"results": [one_item]}; the reducer concatenates them.
    results: Annotated[list, operator.add]


class WorkerInput(TypedDict):
    item: str


def orchestrator(state: State) -> dict:
    return {"items": [f"task-{i}" for i in range(5)]}


def assign(state: State) -> list:
    return [Send("worker", {"item": it}) for it in state["items"]]


def worker(payload: WorkerInput) -> dict:
    # Worker writes ONLY its own result. It never touches other workers' data,
    # so there's no race — the reducer owns the merge.
    return {"results": [f"{payload['item']} -> ok"]}


def collect(state: State) -> dict:
    print(f"  {len(state['results'])} workers wrote results; none lost:")
    for r in sorted(state["results"]):
        print(f"    - {r}")
    return {}


builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("worker", worker)
builder.add_node("collect", collect)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", assign, ["worker"])
builder.add_edge("worker", "collect")
builder.add_edge("collect", END)
graph = builder.compile()


if __name__ == "__main__":
    print("\n5 workers writing one shared 'results' key, merged by a reducer:\n")
    graph.invoke({"results": []})
    print("\nEach worker writes only its own slice -> no race condition.")
