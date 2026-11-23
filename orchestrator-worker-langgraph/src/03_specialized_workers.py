"""
Example 3 — Building specialized workers.

Workers don't have to be identical. A real orchestrator routes each subtask to the
RIGHT KIND of worker — a researcher, a writer, a fact-checker — each with its own
prompt and tools. Here we build three specialized workers and a tiny dispatcher that
picks one per subtask by its declared 'kind'.

Run:
    python src/03_specialized_workers.py
"""
from langchain.agents import create_agent

from llm import MODEL

# Each worker is a focused agent. In a real system each could carry its own tools.
research_worker = create_agent(
    model=MODEL, tools=[],
    system_prompt="You are a researcher. Give 2-3 factual bullet points on the topic.",
)
writer_worker = create_agent(
    model=MODEL, tools=[],
    system_prompt="You are a writer. Produce one polished paragraph on the topic.",
)
critic_worker = create_agent(
    model=MODEL, tools=[],
    system_prompt="You are a critic. Give 2 risks or counterpoints on the topic.",
)

WORKERS = {"research": research_worker, "write": writer_worker, "critique": critic_worker}


def dispatch(kind: str, task: str) -> str:
    """Send a subtask to the specialized worker of the given kind."""
    agent = WORKERS.get(kind, writer_worker)
    result = agent.invoke({"messages": [{"role": "user", "content": task}]})
    return result["messages"][-1].content.strip()


if __name__ == "__main__":
    # The orchestrator would assign a 'kind' to each subtask; here we show all three.
    subtasks = [
        ("research", "the benefits of multi-agent systems"),
        ("write", "an intro paragraph about multi-agent systems"),
        ("critique", "deploying multi-agent systems in production"),
    ]
    for kind, task in subtasks:
        print(f"\n[{kind} worker] {task}")
        print(dispatch(kind, task))
