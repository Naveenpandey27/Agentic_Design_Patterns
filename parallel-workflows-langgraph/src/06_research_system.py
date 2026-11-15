"""
Example 6 — A real-world multi-agent research system (dynamic fan-out).

The headline use case for parallel workflows:
  1. a PLANNER splits a topic into N subtopics,
  2. N RESEARCHERS investigate them all at once (dynamic fan-out with Send),
  3. an AGGREGATOR synthesizes every sub-report into one briefing.

The number of researchers isn't fixed in advance — it depends on the plan — so we
use LangGraph's Send to fan out to however many subtopics the planner produced.

    plan ──Send(xN)──► research (xN, in parallel) ──► aggregate ──► END

Run:
    python src/06_research_system.py
"""
import operator
from typing import TypedDict, Annotated, List

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from llm import get_llm
from schemas import SubReport

llm = get_llm()


class Plan(BaseModel):
    subtopics: List[str] = Field(description="3-4 distinct subtopics to research.")


planner_llm = llm.with_structured_output(Plan)
researcher_llm = llm.with_structured_output(SubReport)


class State(TypedDict):
    topic: str
    subtopics: List[str]
    reports: Annotated[List[SubReport], operator.add]   # researchers append here
    briefing: str


class ResearchTask(TypedDict):
    topic: str
    subtopic: str


def plan_node(state: State) -> dict:
    plan = planner_llm.invoke(f"Break this topic into subtopics to research: {state['topic']}")
    print(f"  [plan] {len(plan.subtopics)} subtopics: {plan.subtopics}")
    return {"subtopics": plan.subtopics}


def fan_out(state: State) -> list:
    """Conditional edge: emit one Send per subtopic -> N parallel researchers."""
    return [Send("research", {"topic": state["topic"], "subtopic": st})
            for st in state["subtopics"]]


def research_node(task: ResearchTask) -> dict:
    """One researcher. Receives a Send payload, not the full graph state."""
    report = researcher_llm.invoke(
        f"Research '{task['subtopic']}' in the context of '{task['topic']}'. "
        "Give a short summary and key points."
    )
    print(f"  [research] done: {task['subtopic']}")
    return {"reports": [report]}


def aggregate_node(state: State) -> dict:
    """Fan-in: synthesize all sub-reports into one briefing."""
    blocks = "\n\n".join(
        f"## {r.subtopic}\n{r.summary}\n" + "\n".join(f"- {p}" for p in r.key_points)
        for r in state["reports"]
    )
    briefing = llm.invoke(
        f"Write a tight executive briefing on '{state['topic']}' from these notes:\n\n{blocks}"
    ).content.strip()
    return {"briefing": briefing}


builder = StateGraph(State)
builder.add_node("plan", plan_node)
builder.add_node("research", research_node)
builder.add_node("aggregate", aggregate_node)
builder.add_edge(START, "plan")
builder.add_conditional_edges("plan", fan_out, ["research"])  # dynamic parallel fan-out
builder.add_edge("research", "aggregate")                     # fan in
builder.add_edge("aggregate", END)
graph = builder.compile()


if __name__ == "__main__":
    topic = "how AI agents are changing software engineering"
    print(f"\nTOPIC: {topic}\n")
    result = graph.invoke({"topic": topic, "reports": []})
    print("\n--- EXECUTIVE BRIEFING ---\n")
    print(result["briefing"])
