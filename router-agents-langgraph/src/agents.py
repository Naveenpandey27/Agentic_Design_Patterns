"""
The specialist agents the router dispatches to.

Each is a small, focused agent with only the tools it needs — that focus is the
whole point of routing. A model given three tools for the current task beats one
juggling thirty.
"""
from langchain.agents import create_agent

from tools import get_weather, calculator

MODEL = "openai:gpt-4o-mini"

weather_agent = create_agent(
    model=MODEL,
    tools=[get_weather],
    system_prompt="You are a weather specialist. Use the get_weather tool. Be concise.",
)

math_agent = create_agent(
    model=MODEL,
    tools=[calculator],
    system_prompt="You are a math specialist. Use the calculator tool; never guess numbers.",
)

# The general agent has no tools — it just answers from the model's knowledge.
general_agent = create_agent(
    model=MODEL,
    tools=[],
    system_prompt="You are a helpful general-knowledge assistant. Be concise.",
)

SPECIALISTS = {
    "weather": weather_agent,
    "math": math_agent,
    "general": general_agent,
}


def ask(route: str, question: str) -> str:
    """Send a question to one specialist and return its final answer text."""
    agent = SPECIALISTS[route]
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].content
