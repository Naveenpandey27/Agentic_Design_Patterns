# Sequential Agentic Workflows in Python — with LangGraph & LangChain

Runnable companion code for the article **"Sequential Agentic Workflows: Building Step-by-Step AI Pipelines."**

A **sequential workflow** runs steps in a fixed order, where each step's output
feeds the next — plan → draft → edit. It's the most fundamental agentic pattern:
predictable, debuggable, and the backbone of most real AI pipelines. This repo
builds it from a plain-Python chain up to a validated, retry-safe LangGraph
pipeline, using one running example: a **blog-post generation pipeline**.

> 📝 Companion article: *(add your Medium link here once published)*

---

## What's inside

| File | Pattern | Needs a key? |
|------|---------|:---:|
| [`src/01_basic_sequential.py`](src/01_basic_sequential.py) | Plain-Python sequential chain (plan → draft → edit) | yes |
| [`src/02_multi_agent_sequential.py`](src/02_multi_agent_sequential.py) | The same chain as three focused **agents** | yes |
| [`src/03_langgraph_sequential.py`](src/03_langgraph_sequential.py) | The pipeline as a **LangGraph** graph (linear edges) | yes |
| [`src/04_state_passing.py`](src/04_state_passing.py) | **How state flows** between nodes — watch it grow | **no** |
| [`src/05_real_world_pipeline.py`](src/05_real_world_pipeline.py) | A **real** pipeline: structured outline → draft → SEO polish | yes |
| [`src/06_errors_retries.py`](src/06_errors_retries.py) | **Retries & backoff** around a flaky step | **no** |
| [`src/07_validation_between_steps.py`](src/07_validation_between_steps.py) | A **validation gate** with a revise loop | **no** |
| [`src/08_parallel_vs_sequential.py`](src/08_parallel_vs_sequential.py) | **Parallel** fan-out/fan-in vs. sequential | **no** |
| [`src/09_evaluate_pipeline.py`](src/09_evaluate_pipeline.py) | **Evaluating** the pipeline with an LLM judge | yes |
| [`src/llm.py`](src/llm.py) | Central model setup (swap providers here) | — |
| [`src/schemas.py`](src/schemas.py) | `Outline` + `QualityCheck` Pydantic schemas | — |

Four examples (04, 06, 07, 08) run with **no API key** — start there to see the
graph mechanics instantly.

---

## Quickstart

You'll need **Python 3.10+** (and an OpenAI API key for the LLM examples).

```bash
# 1. clone and enter the repo
git clone https://github.com/<your-username>/sequential-workflows-langgraph.git
cd sequential-workflows-langgraph

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
python src/04_state_passing.py          # no key — watch state flow
python src/08_parallel_vs_sequential.py # no key — see parallel speedup
python src/03_langgraph_sequential.py   # needs key
python src/05_real_world_pipeline.py    # needs key
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
  topic ─► [ plan ] ─► [ draft ] ─► [ edit ] ─► final
             │            │            │
             └── each step reads the shared STATE and writes its part ──┘

  validation gate:   draft ─► validate ──(fail)──► draft (revise loop)
                                        ──(pass)──► finalize
```

- Steps run **in order**; each one's output is the next one's input.
- A shared **state** object carries everything from step to step.
- **Validation gates** catch bad output before it flows downstream.
- **Retries** keep one flaky step from breaking the whole chain.
- Independent steps can run in **parallel** (fan-out / fan-in) for speed.

---

## License

[MIT](LICENSE) — free to use, learn from, and build on.
