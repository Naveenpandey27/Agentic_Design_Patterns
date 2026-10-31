"""
Example 9 — Evaluating a sequential pipeline.

A pipeline has two things worth measuring: does each STEP do its job, and does the
FINAL output meet the bar? This script runs the real content pipeline on a few topics
and uses an LLM judge (structured output) to score each result — the same habit from
the router article, applied to generated content.

Run:
    python src/09_evaluate_pipeline.py
"""
import importlib

from llm import get_llm
from schemas import QualityCheck

# Reuse the real pipeline from example 5.
pipeline = importlib.import_module("05_real_world_pipeline")

judge = get_llm().with_structured_output(QualityCheck)

TOPICS = [
    "why routing beats one giant agent",
    "how to add memory to an AI agent",
    "sequential vs parallel agent workflows",
]


def grade(topic: str, post: str) -> QualityCheck:
    return judge.invoke(
        "You are a strict editor. Score this blog post on clarity, structure, and "
        "whether it delivers on its topic. Pass only genuinely good posts.\n"
        f"Topic: {topic}\n\nPost:\n{post}"
    )


def evaluate() -> None:
    scores = []
    for topic in TOPICS:
        result = pipeline.graph.invoke({"topic": topic})
        verdict = grade(topic, result["final"])
        scores.append(verdict.score)
        mark = "PASS" if verdict.passed else "FAIL"
        print(f"  [{mark}] score={verdict.score:.2f}  {topic}")
        for issue in verdict.issues:
            print(f"         - {issue}")
    print(f"\nAverage quality score: {sum(scores) / len(scores):.2f}")


if __name__ == "__main__":
    evaluate()
