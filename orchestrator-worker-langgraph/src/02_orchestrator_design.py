"""
Example 2 — Designing the orchestrator: structured task decomposition.

The orchestrator's whole job is to split a task into worker-sized pieces. Doing that
with free text is fragile. Instead we force a structured Plan (Pydantic) — a validated
list of Sections — so the dispatch step gets clean, typed subtasks every time.

Run:
    python src/02_orchestrator_design.py
"""
from llm import get_llm
from schemas import Plan

# with_structured_output makes the orchestrator return a validated Plan object.
orchestrator_llm = get_llm().with_structured_output(Plan)


def plan(task: str) -> Plan:
    return orchestrator_llm.invoke(
        "You are an orchestrator. Break the task into 3-5 independent sections, "
        "each small enough for one worker to handle.\n"
        f"Task: {task}"
    )


if __name__ == "__main__":
    task = "Write a report on adopting AI agents in a mid-size company"
    print(f"\nTASK: {task}\n")
    p = plan(task)
    print(f"Orchestrator produced {len(p.sections)} sections:\n")
    for i, s in enumerate(p.sections, 1):
        print(f"  {i}. {s.name}")
        print(f"     -> {s.brief}")
