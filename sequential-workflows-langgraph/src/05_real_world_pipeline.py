"""
Example 5 — A real-world sequential pipeline: topic -> outline -> draft -> SEO polish.

A fuller version with a structured outline (Pydantic), a draft step, and a final
step that rewrites for clarity and adds a one-line meta description. This is the
shape of an actual content pipeline you might run in production.

    START -> plan -> write -> polish -> END

Run:
    python src/05_real_world_pipeline.py
"""
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from llm import get_llm
from schemas import Outline

llm = get_llm()
planner_llm = llm.with_structured_output(Outline)   # structured, validated outline


class State(TypedDict):
    topic: str
    outline: Outline
    draft: str
    final: str
    meta_description: str


def plan_node(state: State) -> dict:
    outline = planner_llm.invoke(
        f"Create a blog-post outline (title + 3-5 sections) for: {state['topic']}"
    )
    print(f"  [plan ] title: {outline.title}  ({len(outline.sections)} sections)")
    return {"outline": outline}


def write_node(state: State) -> dict:
    o = state["outline"]
    sections = "\n".join(f"- {s}" for s in o.sections)
    draft = llm.invoke(
        f"Write a ~250-word blog post titled '{o.title}' covering:\n{sections}"
    ).content
    print(f"  [write] draft words: {len(draft.split())}")
    return {"draft": draft}


def polish_node(state: State) -> dict:
    final = llm.invoke(f"Polish for clarity and flow:\n{state['draft']}").content
    meta = llm.invoke(
        f"Write a single-sentence SEO meta description (<160 chars) for:\n{final}"
    ).content.strip()
    print(f"  [polish] meta: {meta[:60]}...")
    return {"final": final, "meta_description": meta}


builder = StateGraph(State)
builder.add_node("plan", plan_node)
builder.add_node("write", write_node)
builder.add_node("polish", polish_node)
builder.add_edge(START, "plan")
builder.add_edge("plan", "write")
builder.add_edge("write", "polish")
builder.add_edge("polish", END)
graph = builder.compile()


if __name__ == "__main__":
    topic = "practical tips for evaluating LLM agents"
    print(f"\nTOPIC: {topic}\n")
    result = graph.invoke({"topic": topic})
    print("\n--- FINAL POST ---\n")
    print(result["final"])
    print("\nMETA:", result["meta_description"])
