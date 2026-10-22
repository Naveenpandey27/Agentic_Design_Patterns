"""
Example 4 — Multi-step ReAct: the agent chains several tools on its own.

The question needs three tools used in the right order. Nobody tells the agent
the sequence — it reasons its way there. Run with the trace on to watch it.

Run:
    python src/04_multi_step_react.py
"""
from dotenv import load_dotenv
from langchain.agents import create_agent

from tools import get_weather, c_to_fahrenheit, calculator

load_dotenv()

agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather, c_to_fahrenheit, calculator],
    system_prompt=(
        "You are a helpful weather assistant. "
        "Use the tools to look things up and do any maths — don't guess numbers."
    ),
)


if __name__ == "__main__":
    q = (
        "Get the temperature in Mumbai and in Tokyo, convert both to Fahrenheit, "
        "then tell me the difference between the two in Fahrenheit."
    )
    print(f"\nQ: {q}\n")

    # stream the steps so you can see each reason/act/observe turn
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": q}]},
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()
