"""
Example 3 — The sequential pipeline as a LangGraph graph.

Each step is a node; plain edges chain them in order. LangGraph carries the shared
state from node to node, so each step reads what earlier steps wrote.

    START -> plan -> draft -> edit -> END

Run:
    python src/03_langgraph_sequential.py
"""
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from llm import get_llm

llm = get_llm()


class State(TypedDict):
    topic: str
    outline: str
    draft: str
    final: str


def plan_node(state: State) -> dict:
    outline = llm.invoke(f"4-bullet outline for a post about: {state['topic']}").content
    return {"outline": outline}


def draft_node(state: State) -> dict:
    draft = llm.invoke(f"Write a 150-word draft from this outline:\n{state['outline']}").content
    return {"draft": draft}


def edit_node(state: State) -> dict:
    final = llm.invoke(f"Polish this draft, keep it concise:\n{state['draft']}").content
    return {"final": final}


builder = StateGraph(State)
builder.add_node("plan", plan_node)
builder.add_node("draft", draft_node)
builder.add_node("edit", edit_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "draft")   # linear chain: each edge is one hop
builder.add_edge("draft", "edit")
builder.add_edge("edit", END)

graph = builder.compile()


if __name__ == "__main__":
    topic = "why state matters in agentic workflows"
    print(f"\nTOPIC: {topic}\n")
    result = graph.invoke({"topic": topic})
    print(result["final"])
