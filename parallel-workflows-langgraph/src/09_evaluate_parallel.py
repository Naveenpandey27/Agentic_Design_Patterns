"""
Example 9 — Evaluating a parallel workflow: correctness AND speedup.

A parallel workflow has two things to measure: did it produce the right result
(same quality as sequential), and was it actually faster? This script runs the same
set of independent tasks sequentially and in parallel, checks the outputs match, and
reports the speedup. (Runs offline with simulated work; swap in real LLM calls to
measure your own pipeline.)

Run:
    python src/09_evaluate_parallel.py
"""
import asyncio
import time

TASKS = ["alpha", "beta", "gamma", "delta"]


async def do_work(name: str) -> str:
    await asyncio.sleep(0.4)          # stand-in for a model/API call
    return name.upper()


async def run_sequential() -> list:
    return [await do_work(t) for t in TASKS]


async def run_parallel() -> list:
    return await asyncio.gather(*(do_work(t) for t in TASKS))


async def main() -> None:
    t0 = time.perf_counter(); seq = await run_sequential(); seq_t = time.perf_counter() - t0
    t0 = time.perf_counter(); par = await run_parallel(); par_t = time.perf_counter() - t0

    # 1. correctness: parallel must produce the same results as sequential
    same = sorted(seq) == sorted(par)
    print(f"correctness: {'PASS' if same else 'FAIL'}  (parallel == sequential output)")

    # 2. performance: how much faster?
    print(f"sequential: {seq_t:.2f}s")
    print(f"parallel:   {par_t:.2f}s")
    print(f"speedup:    {seq_t / par_t:.1f}x  over {len(TASKS)} tasks")
    print("\nRule of thumb: ideal speedup ≈ number of independent tasks, minus overhead.")


if __name__ == "__main__":
    asyncio.run(main())
