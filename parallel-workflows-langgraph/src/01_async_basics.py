"""
Example 1 — Concurrency fundamentals with asyncio (runs offline, no API key).

Parallel workflows rest on one Python idea: while one task waits (for a model, an
API, the network), another can run. asyncio.gather launches many awaitables at once
and waits for all of them. This is the engine under every parallel example here.

Run:
    python src/01_async_basics.py
"""
import asyncio
import time


async def fake_work(name: str, seconds: float) -> str:
    """Pretend to call a slow API that mostly waits."""
    print(f"  start  {name}")
    await asyncio.sleep(seconds)          # non-blocking wait -> others can run
    print(f"  finish {name}")
    return f"{name} done"


async def sequential() -> None:
    t0 = time.perf_counter()
    for i in range(3):
        await fake_work(f"task-{i}", 0.5)   # one after another
    print(f"  sequential total: {time.perf_counter() - t0:.2f}s\n")


async def parallel() -> None:
    t0 = time.perf_counter()
    # launch all three at once; gather waits for every one
    results = await asyncio.gather(*(fake_work(f"task-{i}", 0.5) for i in range(3)))
    print(f"  results: {results}")
    print(f"  parallel total: {time.perf_counter() - t0:.2f}s")


async def main() -> None:
    print("\nSEQUENTIAL (one at a time):")
    await sequential()
    print("PARALLEL (all at once with asyncio.gather):")
    await parallel()
    print("\n~1.5s vs ~0.5s — the waits overlapped instead of stacking up.")


if __name__ == "__main__":
    asyncio.run(main())
