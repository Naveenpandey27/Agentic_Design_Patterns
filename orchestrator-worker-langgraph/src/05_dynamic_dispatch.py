"""
Example 5 — Dynamic worker dispatch with LangGraph (the full pattern).

Puts it all together with real LLM calls:
  orchestrator (plan sections) ──Send×N──► worker (write each) ──► synthesizer ──► END

The orchestrator decides how many workers to spawn; Send dispatches one per section;
a reducer collects their outputs; the synthesizer merges them into one document.

Run:
    python src/05_dynamic_dispatch.py
"""
import operator
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from llm import get_llm
from schemas import Plan, Section

llm = get_llm()
orchestrator_llm = llm.with_structured_output(Plan)


class State(TypedDict):
    task: str
    sections: list
    drafts: Annotated[list, operator.add]   # workers append their section drafts
    final: str


class WorkerInput(TypedDict):
    section: Section


def orchestrator(state: State) -> dict:
    plan = orchestrator_llm.invoke(f"Break into 3-4 sections: {state['task']}")
    print(f"  orchestrator -> {[s.name for s in plan.sections]}")
    return {"sections": plan.sections}


def assign_workers(state: State) -> list:
    return [Send("worker", {"section": s}) for s in state["sections"]]


def worker(payload: WorkerInput) -> dict:
    s = payload["section"]
    text = llm.invoke(f"Write a short section '{s.name}'. {s.brief}").content.strip()
    print(f"    worker done: {s.name}")
    return {"drafts": [f"## {s.name}\n{text}"]}


def synthesizer(state: State) -> dict:
    body = "\n\n".join(state["drafts"])
    final = llm.invoke(f"Lightly edit into one coherent document:\n\n{body}").content.strip()
    return {"final": final}


builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("worker", worker)
builder.add_node("synthesizer", synthesizer)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", assign_workers, ["worker"])
builder.add_edge("worker", "synthesizer")
builder.add_edge("synthesizer", END)
graph = builder.compile()


if __name__ == "__main__":
    task = "an explainer on vector databases for engineers"
    print(f"\nTASK: {task}\n")
    result = graph.invoke({"task": task, "drafts": []})
    print("\n--- FINAL DOCUMENT ---\n")
    print(result["final"])
