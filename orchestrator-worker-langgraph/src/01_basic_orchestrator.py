"""
Example 1 — A basic orchestrator-worker system in plain Python.

The core loop with no framework: an ORCHESTRATOR breaks a task into subtasks, a set
of WORKERS each handle one subtask, and the orchestrator stitches the results back
together. Everything else in this repo is a more capable version of this.

Run:
    python src/01_basic_orchestrator.py
"""
from llm import get_llm

llm = get_llm()


def orchestrator(task: str) -> list[str]:
    """Break the task into a handful of subtasks (one per line)."""
    out = llm.invoke(
        f"Break this into 3 short, independent subtasks, one per line, no numbering:\n{task}"
    ).content
    return [line.strip("-• ").strip() for line in out.splitlines() if line.strip()]


def worker(subtask: str) -> str:
    """One worker handles one subtask."""
    return llm.invoke(f"Write 2 concise sentences on: {subtask}").content.strip()


def synthesize(task: str, results: list[str]) -> str:
    """The orchestrator combines the workers' outputs into one answer."""
    joined = "\n\n".join(results)
    return llm.invoke(
        f"Combine these into one coherent paragraph answering '{task}':\n\n{joined}"
    ).content.strip()


def run(task: str) -> str:
    subtasks = orchestrator(task)                 # 1. decompose
    print(f"  orchestrator -> {len(subtasks)} subtasks: {subtasks}")
    results = [worker(st) for st in subtasks]     # 2. workers handle each
    return synthesize(task, results)              # 3. aggregate


if __name__ == "__main__":
    task = "Explain the trade-offs of using microservices"
    print(f"\nTASK: {task}\n")
    print(run(task))
