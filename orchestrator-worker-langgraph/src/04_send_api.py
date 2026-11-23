"""
Example 4 — Understanding LangGraph's Send API (runs offline, no API key).

The orchestrator-worker pattern needs to dispatch a DYNAMIC number of workers —
however many subtasks the orchestrator produced. A normal edge can't do that; it
points to a fixed node. Send can: it says "run node X with THIS payload", and you can
emit a whole list of them, one per subtask.

This example uses deterministic (non-LLM) nodes so you can run it instantly and see
how one orchestrator node fans out to N worker runs via Send.

Run:
    python src/04_send_api.py
"""
import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send


class State(TypedDict):
    subtasks: list
    results: Annotated[list, operator.add]   # reducer collects worker outputs


class WorkerInput(TypedDict):
    subtask: str


def orchestrator(state: State) -> dict:
    # Pretend the orchestrator decomposed a task into these subtasks.
    subtasks = ["intro", "body", "conclusion"]
    print(f"  orchestrator -> {subtasks}")
    return {"subtasks": subtasks}


def assign_workers(state: State) -> list:
    """The heart of dynamic dispatch: one Send per subtask -> N worker runs."""
    return [Send("worker", {"subtask": st}) for st in state["subtasks"]]


def worker(payload: WorkerInput) -> dict:
    """One worker run. Receives just its Send payload, not the whole state."""
    print(f"    worker handling: {payload['subtask']}")
    return {"results": [f"done: {payload['subtask']}"]}


def collect(state: State) -> dict:
    print(f"  collected {len(state['results'])} worker results: {state['results']}")
    return {}


builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("worker", worker)
builder.add_node("collect", collect)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", assign_workers, ["worker"])  # dynamic fan-out
builder.add_edge("worker", "collect")
builder.add_edge("collect", END)
graph = builder.compile()


if __name__ == "__main__":
    print("\nOne orchestrator node fans out to N workers via Send:\n")
    graph.invoke({"results": []})
    print("\nSend is what makes the worker count dynamic — decided at runtime.")
