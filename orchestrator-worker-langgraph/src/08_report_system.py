"""
Example 8 — A real-world multi-agent report system.

The canonical orchestrator-worker use case: generate a full report.
  1. ORCHESTRATOR reads the topic and plans the sections (dynamic — it decides how many)
  2. WORKERS each research-and-write one section, in parallel (Send)
  3. SYNTHESIZER assembles the sections into one coherent report with an intro

This is the same backbone as a "deep research" agent.

    orchestrator ──Send×N──► section_worker (parallel) ──► synthesizer ──► END

Run:
    python src/08_report_system.py
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
    topic: str
    sections: list
    completed: Annotated[list, operator.add]   # (index, heading, body) per worker
    report: str


class SectionTask(TypedDict):
    index: int
    section: Section


def orchestrator(state: State) -> dict:
    """Plan the report: decide the sections dynamically."""
    plan = orchestrator_llm.invoke(
        f"Plan a concise report on '{state['topic']}'. "
        "Produce 3-4 sections that together cover it well."
    )
    print(f"  [orchestrator] planned {len(plan.sections)} sections: "
          f"{[s.name for s in plan.sections]}")
    return {"sections": plan.sections}


def assign_workers(state: State) -> list:
    """Dispatch one worker per planned section."""
    return [Send("section_worker", {"index": i, "section": s})
            for i, s in enumerate(state["sections"])]


def section_worker(task: SectionTask) -> dict:
    """One worker writes one section."""
    s = task["section"]
    body = llm.invoke(
        f"Write a focused ~120-word section titled '{s.name}'. Cover: {s.brief}"
    ).content.strip()
    print(f"  [worker] finished: {s.name}")
    return {"completed": [(task["index"], s.name, body)]}


def synthesizer(state: State) -> dict:
    """Assemble sections in order and add a short intro."""
    ordered = sorted(state["completed"], key=lambda t: t[0])
    body = "\n\n".join(f"## {name}\n{text}" for _, name, text in ordered)
    intro = llm.invoke(
        f"Write a 2-sentence introduction for a report on '{state['topic']}'."
    ).content.strip()
    return {"report": f"# {state['topic'].title()}\n\n{intro}\n\n{body}"}


builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("section_worker", section_worker)
builder.add_node("synthesizer", synthesizer)
builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", assign_workers, ["section_worker"])
builder.add_edge("section_worker", "synthesizer")
builder.add_edge("synthesizer", END)
graph = builder.compile()


if __name__ == "__main__":
    topic = "how AI agents are changing software engineering"
    print(f"\nTOPIC: {topic}\n")
    result = graph.invoke({"topic": topic, "completed": []})
    print("\n" + "=" * 60 + "\n")
    print(result["report"])
