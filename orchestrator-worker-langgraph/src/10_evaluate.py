"""
Example 10 — Evaluating orchestrator-worker performance (runs offline, no API key).

Two things decide whether an orchestrator-worker system is any good:
  1. COVERAGE  — did the workers' sections actually cover the task (no gaps/overlap)?
  2. COMPLETION — did every dispatched worker return a usable result?

This harness checks both on a simulated run. Swap in your real graph and an LLM judge
to grade coverage on live output.

Run:
    python src/10_evaluate.py
"""

# Simulated orchestrator output: what the orchestrator planned vs. what workers returned.
PLANNED = ["Introduction", "Core Concepts", "Trade-offs", "Conclusion"]
RETURNED = {
    "Introduction": "ok",
    "Core Concepts": "ok",
    "Trade-offs": "ok",
    "Conclusion": "[unavailable]",   # one worker degraded
}

# A tiny rubric of points the task should cover (in a real eval, an LLM judge checks this).
EXPECTED_COVERAGE = {"what it is", "how it works", "pros and cons", "summary"}
ACTUAL_COVERAGE = {"what it is", "how it works", "pros and cons"}  # 'summary' missing


def evaluate() -> None:
    # 1. completion: how many workers returned usable output?
    done = [s for s in PLANNED if RETURNED.get(s, "").strip() and RETURNED[s] != "[unavailable]"]
    completion = len(done) / len(PLANNED)
    print(f"completion: {len(done)}/{len(PLANNED)} workers succeeded = {completion:.0%}")
    for s in PLANNED:
        mark = "ok " if s in done else "XX "
        print(f"  {mark} {s}")

    # 2. coverage: did the plan cover the expected points?
    covered = EXPECTED_COVERAGE & ACTUAL_COVERAGE
    coverage = len(covered) / len(EXPECTED_COVERAGE)
    missing = EXPECTED_COVERAGE - ACTUAL_COVERAGE
    print(f"\ncoverage: {len(covered)}/{len(EXPECTED_COVERAGE)} points = {coverage:.0%}")
    if missing:
        print(f"  gaps the orchestrator missed: {missing}")

    print("\nTrack both over time: completion catches worker failures, "
          "coverage catches bad decomposition.")


if __name__ == "__main__":
    evaluate()
