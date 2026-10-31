"""
Example 2 — A sequential workflow of multiple agents.

Same plan -> draft -> edit pipeline, but each step is now a focused agent with its
own role (and could have its own tools). The handoff is still simple: one agent's
output is the next agent's input.

Run:
    python src/02_multi_agent_sequential.py
"""
from langchain.agents import create_agent

from llm import MODEL

planner = create_agent(
    model=MODEL, tools=[],
    system_prompt="You are a content planner. Output a tight 4-point outline, nothing else.",
)
writer = create_agent(
    model=MODEL, tools=[],
    system_prompt="You are a writer. Turn the given outline into a ~150-word draft.",
)
editor = create_agent(
    model=MODEL, tools=[],
    system_prompt="You are an editor. Tighten the given draft; fix flow and clarity.",
)


def ask(agent, text: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": text}]})
    return result["messages"][-1].content


def run(topic: str) -> str:
    outline = ask(planner, f"Topic: {topic}")
    draft = ask(writer, outline)
    final = ask(editor, draft)
    return final


if __name__ == "__main__":
    topic = "how sequential AI pipelines reduce errors"
    print(f"\nTOPIC: {topic}\n")
    print(run(topic))
