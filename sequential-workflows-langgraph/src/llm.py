"""
Central model setup, so every example uses the same configuration and switching
providers is a one-line change here.
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()  # reads OPENAI_API_KEY from your .env

MODEL = "openai:gpt-4o-mini"
# To use Claude instead:  pip install langchain-anthropic
#   MODEL = "anthropic:claude-haiku-4-5"   (and set ANTHROPIC_API_KEY in .env)


def get_llm(model: str = MODEL):
    """Return a chat model instance."""
    return init_chat_model(model)
