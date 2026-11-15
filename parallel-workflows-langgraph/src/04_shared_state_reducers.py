"""
Example 4 — Shared state, reducers, and race conditions (runs offline, no API key).

When several nodes write the SAME state key at the SAME time, who wins? Without a
reducer, concurrent writes conflict — that's a race condition. A reducer tells
LangGraph how to MERGE concurrent writes instead of overwriting. This example shows
the safe pattern (list + operator.add) and explains the unsafe one.

Run:
    python src/04_shared_state_reducers.py
"""
import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    # SAFE: the reducer concatenates whatever each parallel branch returns.
    results: Annotated[list, operator.add]
    # A plain `results: list` here would raise InvalidUpdateError when two parallel
    # branches both write it — LangGraph won't silently pick a winner.


def worker_a(state: State) -> dict:
    return {"results": ["A finished"]}


def worker_b(state: State) -> dict:
    return {"results": ["B finished"]}


def worker_c(state: State) -> dict:
    return {"results": ["C finished"]}


def collect(state: State) -> dict:
    print("All parallel writes merged safely by the reducer:")
    for r in sorted(state["results"]):
        print(f"  - {r}")
    print(f"\n  total items: {len(state['results'])}  (none lost to a race)")
    return {}


builder = StateGraph(State)
for name, fn in [("A", worker_a), ("B", worker_b), ("C", worker_c)]:
    builder.add_node(name, fn)
builder.add_node("collect", collect)
for name in ("A", "B", "C"):
    builder.add_edge(START, name)       # three branches write 'results' at once
    builder.add_edge(name, "collect")
builder.add_edge("collect", END)
graph = builder.compile()


if __name__ == "__main__":
    print("\nThree parallel workers all write the same 'results' key:\n")
    graph.invoke({"results": []})
    print("\nThe reducer (operator.add) is what makes concurrent writes safe.")
