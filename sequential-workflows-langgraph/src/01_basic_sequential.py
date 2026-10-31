"""
Example 1 — A basic sequential workflow in plain Python.

Three LLM calls in a fixed order: plan -> draft -> edit. The output of each step
becomes the input of the next. No framework — just functions, so you can see the
whole idea with nothing hidden.

Run:
    python src/01_basic_sequential.py
"""
from llm import get_llm

llm = get_llm()


def plan(topic: str) -> str:
    """Step 1: turn a topic into a short outline."""
    return llm.invoke(
        f"Write a 4-bullet outline for a short blog post about: {topic}"
    ).content


def draft(outline: str) -> str:
    """Step 2: turn the outline into a draft."""
    return llm.invoke(
        f"Write a 150-word draft blog post following this outline:\n{outline}"
    ).content


def edit(draft_text: str) -> str:
    """Step 3: polish the draft."""
    return llm.invoke(
        f"Tighten and polish this draft. Keep it concise:\n{draft_text}"
    ).content


def run(topic: str) -> str:
    outline = plan(topic)        # each step's output
    draft_text = draft(outline)  # feeds the next step's input
    final = edit(draft_text)
    return final


if __name__ == "__main__":
    topic = "why small AI agents beat one giant agent"
    print(f"\nTOPIC: {topic}\n")
    print(run(topic))
