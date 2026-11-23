"""
Example 9 — Worker failures, retries, and timeouts (runs offline, no API key).

With many workers, some will fail or hang. A robust orchestrator-worker system makes
each WORKER responsible for its own recovery: retry transient errors, time out slow
calls, and return a safe placeholder instead of crashing. One dead worker must not
sink the whole report — the synthesizer should still assemble the sections that
succeeded.

Run:
    python src/09_failures_timeouts.py
"""
import operator
import random
import time
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

MAX_RETRIES = 3


class State(TypedDict):
    sections: list
    completed: Annotated[list, operator.add]
    report: str


class WorkerInput(TypedDict):
    name: str


def flaky_write(name: str) -> str:
    """Simulate a worker call that may fail."""
    if random.random() < 0.5:
        raise ConnectionError("simulated timeout")
    return f"content for {name}"


def worker(payload: WorkerInput) -> dict:
    """Each worker retries with backoff, then degrades to a placeholder."""
    name = payload["name"]
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            text = flaky_write(name)
            return {"completed": [(name, text)]}
        except Exception as exc:  # noqa: BLE001
            print(f"    [{name}] attempt {attempt} failed ({exc})")
            time.sleep(0.05 * attempt)
    # retries exhausted -> safe placeholder, so the report still assembles
    print(f"    [{name}] gave up -> placeholder")
    return {"completed": [(name, "[section unavailable]")]}


def orchestrator(state: State) -> dict:
    return {"sections": ["Overview", "Benefits", "Risks", "Outlook"]}


def assign(state: State) -> list:
    return [Send("worker", {"name": n}) for n in state["sections"]]


def synthesizer(state: State) -> dict:
    ok = [n for n, t in state["completed"] if t != "[section unavailable]"]
    missing = [n for n, t in state["completed"] if t == "[section unavailable]"]
    print(f"\n  assembled {len(ok)} sections; {len(missing)} degraded: {missing}")
    return {"report": "\n".join(f"## {n}\n{t}" for n, t in state["completed"])}


builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("worker", worker)
builder.add_node("synthesizer", synthesizer)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", assign, ["worker"])
builder.add_edge("worker", "synthesizer")
builder.add_edge("synthesizer", END)
graph = builder.compile()


if __name__ == "__main__":
    random.seed(3)
    print("\nWorkers retry, time out, and degrade — the report still assembles:\n")
    result = graph.invoke({"completed": []})
    print("\n--- REPORT ---\n")
    print(result["report"])
