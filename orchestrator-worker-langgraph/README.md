# Orchestrator-Worker Agents in Python — with LangGraph & LangChain

Runnable companion code for the article **"Orchestrator-Worker Agents: Dynamic Task Decomposition with AI."**

In the **orchestrator-worker** pattern, a lead agent (the *orchestrator*) breaks a
complex task into subtasks **at runtime**, dispatches a *worker* to each one, and
synthesizes their results into a final answer. Unlike a plain parallel workflow
(where the branches are fixed in advance), the orchestrator decides **how many
workers and what each one does** based on the task itself. This repo builds it from
a plain-Python loop up to a real multi-agent report generator, using LangGraph's
`Send` API for dynamic dispatch.

> 📝 Companion article: *(add your Medium link here once published)*

---

## What's inside

| File | Topic | Needs a key? |
|------|-------|:---:|
| [`src/01_basic_orchestrator.py`](src/01_basic_orchestrator.py) | The whole pattern in plain Python | yes |
| [`src/02_orchestrator_design.py`](src/02_orchestrator_design.py) | Structured task decomposition (Pydantic `Plan`) | yes |
| [`src/03_specialized_workers.py`](src/03_specialized_workers.py) | Heterogeneous workers (researcher / writer / critic) | yes |
| [`src/04_send_api.py`](src/04_send_api.py) | LangGraph's **`Send`** API — dynamic dispatch | **no** |
| [`src/05_dynamic_dispatch.py`](src/05_dynamic_dispatch.py) | The full graph: orchestrator → Send×N → synthesizer | yes |
| [`src/06_shared_state.py`](src/06_shared_state.py) | Shared state + reducers (safe worker writes) | **no** |
| [`src/07_aggregation.py`](src/07_aggregation.py) | Aggregating worker outputs **in order** | **no** |
| [`src/08_report_system.py`](src/08_report_system.py) | **Real** multi-agent report generator | yes |
| [`src/09_failures_timeouts.py`](src/09_failures_timeouts.py) | Worker retries, timeouts, graceful degradation | **no** |
| [`src/10_evaluate.py`](src/10_evaluate.py) | Evaluating coverage + completion | **no** |
| [`src/llm.py`](src/llm.py) | Central model setup (swap providers here) | — |
| [`src/schemas.py`](src/schemas.py) | `Section` + `Plan` Pydantic schemas | — |

Five examples (04, 06, 07, 09, 10) run with **no API key** — start there to see the
dispatch mechanics instantly.

---

## Quickstart

You'll need **Python 3.10+** (and an OpenAI API key for the LLM examples).

```bash
git clone https://github.com/<your-username>/orchestrator-worker-langgraph.git
cd orchestrator-worker-langgraph

python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env             # then add your key (LLM examples only)
```

Run the no-key examples first, then the rest:

```bash
python src/04_send_api.py          # no key — see dynamic dispatch
python src/07_aggregation.py       # no key — ordered aggregation
python src/09_failures_timeouts.py # no key — worker failure handling
python src/08_report_system.py     # needs key — the full report generator
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
                    ┌─► worker (section 1) ─┐
  task ─► ORCHESTRATOR ─► worker (section 2) ─┼─► SYNTHESIZER ─► result
          (plan, decide N) └─► worker (section 3) ─┘   (combine)
                 │
         decides how many workers and what each does — at runtime
```

- The **orchestrator** decomposes the task dynamically (not fixed in advance).
- **`Send`** dispatches one worker per subtask — however many there are.
- A **reducer** lets all workers write results safely (no race conditions).
- The **synthesizer** waits for every worker, then assembles one answer.

---

## License

[MIT](LICENSE) — free to use, learn from, and build on.
