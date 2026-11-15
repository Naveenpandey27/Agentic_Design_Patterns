"""
Example 7 — Failures, retries, and timeouts in parallel (runs offline, no API key).

In a parallel workflow one branch failing shouldn't sink the others. The pattern:
give each task a timeout, catch its errors, and return partial results — the branches
that succeeded still count. asyncio.gather(return_exceptions=True) is the key: it
collects exceptions instead of cancelling the whole batch.

Run:
    python src/07_failures_timeouts.py
"""
import asyncio
import random


async def flaky_task(name: str) -> str:
    """Simulates a task that may be slow or may fail."""
    delay = random.choice([0.2, 0.3, 2.0])        # 2.0 will blow the timeout
    if random.random() < 0.25:
        raise RuntimeError("simulated API error")
    await asyncio.sleep(delay)
    return f"{name}: ok ({delay}s)"


async def run_with_timeout(name: str, timeout: float = 1.0) -> str:
    """Wrap one task with a timeout and turn any failure into a value, not a crash."""
    try:
        return await asyncio.wait_for(flaky_task(name), timeout=timeout)
    except asyncio.TimeoutError:
        return f"{name}: TIMEOUT (skipped)"
    except Exception as exc:  # noqa: BLE001
        return f"{name}: FAILED ({exc})"


async def main() -> None:
    tasks = [run_with_timeout(f"task-{i}") for i in range(6)]
    # return_exceptions=True: one bad task never cancels the batch
    results = await asyncio.gather(*tasks, return_exceptions=True)

    print("Per-branch outcome (failures isolated, successes kept):")
    ok = 0
    for r in results:
        print(f"  - {r}")
        ok += isinstance(r, str) and r.endswith(")") and "ok" in r
    print(f"\n  {ok}/{len(results)} branches succeeded; the rest degraded gracefully.")


if __name__ == "__main__":
    random.seed(7)
    asyncio.run(main())
