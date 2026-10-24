# Router Agents in Python — with LangGraph & LangChain

Runnable companion code for the article **"Router Agents: Building Intelligent AI Systems That Choose the Right Tool or Agent."**

A **router agent** is the receptionist of an AI system: it looks at an incoming
query and decides *who should handle it* — which tool, which specialist agent,
which lane — before any real work happens. This repo builds that idea up from a
10-line keyword matcher to a confidence-aware multi-agent system, all using one
consistent example: a personal assistant that routes between **weather**,
**math**, and **general** lanes.

> 📝 Companion article: *(add your Medium link here once published)*

---

## What's inside

| File | Pattern |
|------|---------|
| [`src/01_rule_based_router.py`](src/01_rule_based_router.py) | **Rule-based** routing — keyword matching, no LLM. The baseline. |
| [`src/02_llm_router.py`](src/02_llm_router.py) | **LLM** router — the model classifies the query (understands meaning). |
| [`src/03_structured_router.py`](src/03_structured_router.py) | **Structured** routing — `with_structured_output` + Pydantic (route + confidence + reasoning). |
| [`src/04_langgraph_router.py`](src/04_langgraph_router.py) | Router as a **LangGraph** node with conditional edges to specialist nodes. |
| [`src/05_multi_agent_router.py`](src/05_multi_agent_router.py) | **Multi-agent** router — dispatches to real tool-using specialist agents. |
| [`src/06_confidence_fallback_router.py`](src/06_confidence_fallback_router.py) | **Confidence thresholds, fallbacks & ambiguity** — ask instead of guessing. |
| [`src/07_evaluate_router.py`](src/07_evaluate_router.py) | **Evaluating** the router — treat it like a classifier, measure accuracy. |
| [`src/tools.py`](src/tools.py) | Shared demo tools (fake/offline, so it runs with no setup). |
| [`src/agents.py`](src/agents.py) | The specialist agents the router dispatches to. |
| [`src/router_schemas.py`](src/router_schemas.py) | `ROUTES` + the `RouteDecision` Pydantic schema. |

Read them in order — each one builds on the last.

---

## Quickstart

You'll need **Python 3.10+** and an OpenAI API key.

```bash
# 1. clone and enter the repo
git clone https://github.com/<your-username>/router-agents-langgraph.git
cd router-agents-langgraph

# 2. (recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. add your API key
cp .env.example .env             # then open .env and paste your key
```

Run any example (example 1 needs no key at all):

```bash
python src/01_rule_based_router.py       # no API key needed
python src/03_structured_router.py
python src/05_multi_agent_router.py
python src/07_evaluate_router.py
```

---

## Prefer Claude (or another provider)?

Everything uses LangChain's provider-agnostic `init_chat_model` / `create_agent`,
so switching is a one-line change:

```bash
pip install langchain-anthropic
```

Add `ANTHROPIC_API_KEY` to your `.env`, then change the model string
(e.g. in `src/agents.py` and each router) from `"openai:gpt-4o-mini"` to
`"anthropic:claude-haiku-4-5"`. Any provider LangChain supports works the same way.

---

## The core idea in one picture

```
                         ┌─► weather specialist  (get_weather)
   query ─► ROUTER ──────┼─► math specialist     (calculator)
            (classify)   └─► general specialist  (no tools)
               │
         low confidence? ─► ask the user to clarify (don't guess)
```

- The router **classifies** — it doesn't answer. It picks a lane.
- Each **specialist** is small and focused, with only the tools it needs.
- A **confidence score** lets the router ask instead of guessing wrong.
- You **evaluate** it like any classifier: labeled set in, accuracy out.

---

## License

[MIT](LICENSE) — free to use, learn from, and build on.
