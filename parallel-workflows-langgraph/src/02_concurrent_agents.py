"""
Example 2 — Running multiple LLM calls concurrently.

The simplest real parallel workflow: ask the model several independent questions at
once with asyncio.gather, instead of waiting for each in turn. Three questions that
each take ~1s finish in ~1s total, not ~3s.

Run:
    python src/02_concurrent_agents.py
"""
import asyncio
import time

from llm import get_llm

llm = get_llm()

QUESTIONS = [
    "In one sentence, what is parallelism in computing?",
    "In one sentence, what is a race condition?",
    "In one sentence, what is a semaphore?",
]


async def ask(question: str) -> str:
    # ainvoke is the async version of invoke — it awaits instead of blocking.
    resp = await llm.ainvoke(question)
    return resp.content.strip()


async def main() -> None:
    t0 = time.perf_counter()
    answers = await asyncio.gather(*(ask(q) for q in QUESTIONS))   # all at once
    for q, a in zip(QUESTIONS, answers):
        print(f"Q: {q}\nA: {a}\n")
    print(f"3 model calls, concurrently, in {time.perf_counter() - t0:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
