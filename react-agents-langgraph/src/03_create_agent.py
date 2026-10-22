"""
Example 3 — The production one-liner: create_agent.

LangChain 1.0's create_agent builds the whole ReAct loop for you. This is the
version you'd actually ship. (It replaces the older
langgraph.prebuilt.create_react_agent.)

Run:
    python src/03_create_agent.py
"""
from dotenv import load_dotenv
from langchain.agents import create_agent

from tools import get_weather, c_to_fahrenheit

load_dotenv()

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather, c_to_fahrenheit],
    system_prompt="You are a helpful assistant. Use tools when you need live data.",
)


if __name__ == "__main__":
    q = "What's the weather in Delhi, and what is that in Fahrenheit?"
    print(f"\nQ: {q}\n")
    result = agent.invoke({"messages": [{"role": "user", "content": q}]})
    print("A:", result["messages"][-1].content, "\n")
