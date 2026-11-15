# Parallel Agentic Workflows in Python — with LangGraph & LangChain

Runnable companion code for the article **"Parallel Agentic Workflows: Running Multiple AI Agents Concurrently."**

A **parallel workflow** runs independent steps *at the same time* instead of one
after another — fan out to many agents, then fan in to combine their results. When
steps don't depend on each other, this turns an N-step wait into roughly a one-step
wait. This repo builds it from raw `asyncio` up to a dynamic multi-agent research
system, using one running example: **research a topic with many agents at once.**

> 📝 Companion article: *(add your Medium link here once published)*

---

## What's inside

| File | Pattern | Needs a key? |
|------|---------|:---:|
| [`src/01_async_basics.py`](src/01_async_basics.py) | `asyncio.gather` — the concurrency engine | **no** |
| [`src/02_concurrent_agents.py`](src/02_concurrent_agents.py) | Many **LLM calls at once** (`ainvoke` + gather) | yes |
| [`src/03_langgraph_parallel.py`](src/03_langgraph_parallel.py) | **Fan-out / fan-in** in a LangGraph graph | yes |
| [`src/04_shared_state_reducers.py`](src/04_shared_state_reducers.py) | **Reducers & race conditions** — safe concurrent writes | **no** |
| [`src/05_aggregation_node.py`](src/05_aggregation_node.py) | **Aggregation node** — wait for all, then merge | yes |
| [`src/06_research_system.py`](src/06_research_system.py) | **Real multi-agent research** — dynamic fan-out with `Send` | yes |
| [`src/07_failures_timeouts.py`](src/07_failures_timeouts.py) | **Failures, retries, timeouts** — isolate one bad branch | **no** |
| [`src/08_concurrency_control.py`](src/08_concurrency_control.py) | **Semaphore** — cap how many run at once | **no** |
| [`src/09_evaluate_parallel.py`](src/09_evaluate_parallel.py) | **Evaluate** — correctness + speedup | **no** |
| [`src/llm.py`](src/llm.py) | Central model setup (swap providers here) | — |
| [`src/schemas.py`](src/schemas.py) | `SubReport` Pydantic schema | — |

Five examples (01, 04, 07, 08, 09) run with **no API key** — start there to see the
concurrency mechanics instantly.

---

## Quickstart

You'll need **Python 3.10+** (and an OpenAI API key for the LLM examples).

```bash
# 1. clone and enter the repo
git clone https://github.com/<your-username>/parallel-workflows-langgraph.git
cd parallel-workflows-langgraph

# 2. (recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. add your API key (only needed for the LLM examples)
cp .env.example .env             # then open .env and paste your key
```

Run the no-key examples first, then the rest:

```bash
python src/01_async_basics.py          # no key — see the speedup
python src/04_shared_state_reducers.py # no key — safe concurrent writes
python src/08_concurrency_control.py   # no key — semaphore caps
python src/06_research_system.py       # needs key — the full system
```

---

## Prefer Claude (or another provider)?

Everything routes through `src/llm.py`. Change one line:

```bash
pip install langchain-anthropic
```

```python
# src/llm.py
MODEL = "anthropic:claude-haiku-4-5"   # was "openai:gpt-4o-mini"
```

Add `ANTHROPIC_API_KEY` to your `.env`. Any provider LangChain supports works the same way.

---

## The core idea in one picture

```
  SEQUENTIAL:  A ──► B ──► C          total = A + B + C
                                     
  PARALLEL:    ┌─► A ─┐
          fan ─┼─► B ─┼─ fan-in ►    total ≈ max(A, B, C)
          out  └─► C ─┘  (aggregate)
```

- Independent steps run **at once**, not in a line.
- A **reducer** lets parallel branches write shared state without clobbering (no race conditions).
- An **aggregation node** waits for every branch, then merges the results.
- A **semaphore** caps concurrency so you don't get rate-limited.
- **Timeouts + `return_exceptions`** keep one slow/failed branch from sinking the rest.

---

## License

[MIT](LICENSE) — free to use, learn from, and build on.
