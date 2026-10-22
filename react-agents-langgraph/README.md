# ReAct Agents in Python — with LangGraph & LangChain

Runnable companion code for the article **"ReAct Agents Explained: Reasoning + Acting in AI Agents."**

ReAct is the pattern behind almost every "AI agent" you've heard of: the model
**reasons** about what it needs, **acts** by calling a tool, **observes** the
result, and loops until it can answer. This repo shows that exact loop four
ways — from a hand-written `while` loop up to the one-line production version —
so you can see that they're all the same idea at different altitudes.

> 📝 Companion article: *(add your Medium link here once published)*

---

## What's inside

| File | What it shows |
|------|---------------|
| [`src/01_manual_react_loop.py`](src/01_manual_react_loop.py) | The ReAct loop **by hand** — a plain `while` loop, so you see every Reason → Act → Observe step with nothing hidden. |
| [`src/02_langgraph_react.py`](src/02_langgraph_react.py) | The same loop as a **LangGraph graph** (`StateGraph` + `ToolNode` + `tools_condition`). |
| [`src/03_create_agent.py`](src/03_create_agent.py) | The **production one-liner**: `create_agent` builds the whole loop for you. |
| [`src/04_multi_step_react.py`](src/04_multi_step_react.py) | A **multi-step** task where the agent chains three tools in the right order on its own. |
| [`src/tools.py`](src/tools.py) | The shared demo tools (fake/offline, so the repo runs with no extra setup). |

---

## Quickstart

You'll need **Python 3.10+** and an OpenAI API key.

```bash
# 1. clone and enter the repo
git clone https://github.com/<your-username>/react-agents-langgraph.git
cd react-agents-langgraph

# 2. (recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. add your API key
cp .env.example .env             # then open .env and paste your key
```

Now run any example:

```bash
python src/01_manual_react_loop.py
python src/02_langgraph_react.py
python src/03_create_agent.py
python src/04_multi_step_react.py
```

Each script prints its reasoning trace so you can watch the loop happen.

---

## Prefer Claude (or another provider)?

Everything uses LangChain's provider-agnostic `init_chat_model` / `create_agent`,
so switching is a one-line change:

```bash
pip install langchain-anthropic
```

Add `ANTHROPIC_API_KEY` to your `.env`, then change the model string in any script:

```python
# from
model="openai:gpt-4o-mini"
# to
model="anthropic:claude-haiku-4-5"
```

The same works for other providers LangChain supports (Google, Groq, Ollama, …).

---

## How the loop works (the 10-second version)

```
          ┌─────────── loop while the model keeps asking for tools ───────────┐
          │                                                                     │
  User ─► Agent (REASON) ─► tool call? ──yes──► Tools (ACT + OBSERVE) ─────────┘
                               │
                               no
                               ▼
                         Final answer
```

- **Reason** — the model reads the conversation and decides: answer, or call a tool?
- **Act** — if it wants a tool, it emits the tool name + arguments. *Your code* runs it.
- **Observe** — the result is appended to the conversation and handed back to the model.
- Repeat until the model answers with no tool call.

---

## License

[MIT](LICENSE) — free to use, learn from, and build on.
