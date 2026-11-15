"""
Example 8 — Controlling concurrency with a semaphore (runs offline, no API key).

Unlimited parallelism will get you rate-limited (or bankrupt). You rarely want 100
model calls firing at once. A semaphore caps how many run simultaneously: launch all
the tasks, but only N proceed at a time while the rest wait their turn.

Run:
    python src/08_concurrency_control.py
"""
import asyncio
import time

MAX_CONCURRENCY = 3        # at most 3 in flight at once
TOTAL_TASKS = 9


async def call_api(sem: asyncio.Semaphore, i: int) -> str:
    async with sem:                       # acquire a slot (waits if all taken)
        print(f"  -> task {i} running   ({MAX_CONCURRENCY} max in flight)")
        await asyncio.sleep(0.5)          # pretend this is a model call
        print(f"  <- task {i} done")
        return f"task {i}"


async def main() -> None:
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    t0 = time.perf_counter()
    # all 9 are scheduled, but the semaphore lets only 3 run at a time
    await asyncio.gather(*(call_api(sem, i) for i in range(TOTAL_TASKS)))
    elapsed = time.perf_counter() - t0
    print(f"\n  {TOTAL_TASKS} tasks, max {MAX_CONCURRENCY} at once: {elapsed:.2f}s")
    print(f"  (≈ 3 waves of 0.5s, not {TOTAL_TASKS * 0.5:.1f}s serial, "
          f"nor 0.5s fully-parallel)")


if __name__ == "__main__":
    asyncio.run(main())
