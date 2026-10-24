"""
Example 2 — An LLM-powered router.

Instead of matching keywords, we ask a model to classify the query into one of
our routes. This understands meaning ("how warm is it in Tokyo" -> weather) that
keyword rules miss — but a plain-text answer still needs parsing and can drift
("I think this is weather!"). Example 3 fixes that with structured output.

Run:
    python src/02_llm_router.py
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

from router_schemas import ROUTES

load_dotenv()

llm = init_chat_model("openai:gpt-4o-mini")

ROUTER_PROMPT = (
    "You are a router. Classify the user's query into exactly one of these "
    f"routes: {', '.join(ROUTES)}.\n"
    "Reply with ONLY the route word, nothing else.\n\n"
    "Query: {query}"
)


def route(query: str) -> str:
    raw = llm.invoke(ROUTER_PROMPT.format(query=query)).content.strip().lower()
    # Guard against the model adding stray words — keep only a known route.
    for r in ROUTES:
        if r in raw:
            return r
    return "general"  # fallback if the model says something unexpected


if __name__ == "__main__":
    tests = [
        "How warm is it in Tokyo right now?",   # weather, no keyword match
        "What's seven squared plus ten?",       # math, words not digits
        "Explain photosynthesis in one line.",  # general
    ]
    for q in tests:
        print(f"{route(q):8}  <-  {q}")
