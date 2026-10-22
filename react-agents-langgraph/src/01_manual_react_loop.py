"""
Example 1 — The ReAct loop by hand (no agent framework).

This shows the raw Reason -> Act -> Observe cycle with nothing but a model
and a while loop, so you can see exactly what every agent framework automates.

Run:
    python src/01_manual_react_loop.py
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from tools import get_weather, c_to_fahrenheit

load_dotenv()  # reads OPENAI_API_KEY from your .env

TOOLS = [get_weather, c_to_fahrenheit]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}

# Bind the tools so the model knows they exist and can request them.
llm = init_chat_model("openai:gpt-4o-mini")
llm_with_tools = llm.bind_tools(TOOLS)


def run(question: str, max_steps: int = 5) -> str:
    """Drive the ReAct loop manually until the model stops asking for tools."""
    messages = [
        SystemMessage("You are a helpful assistant. Use tools when you need live data."),
        HumanMessage(question),
    ]

    for step in range(1, max_steps + 1):
        # --- REASON: let the model look at the conversation and decide ---
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        # No tool calls? The model is done reasoning — this is the final answer.
        if not ai_msg.tool_calls:
            return ai_msg.content

        # --- ACT + OBSERVE: run each requested tool, feed the result back ---
        for call in ai_msg.tool_calls:
            print(f"  [step {step}] ACT    -> {call['name']}({call['args']})")
            tool = TOOLS_BY_NAME[call["name"]]
            result = tool.invoke(call["args"])
            print(f"  [step {step}] OBSERVE-> {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))

    return "Stopped: hit the step limit without a final answer."


if __name__ == "__main__":
    q = "What's the weather in Delhi, and what is that temperature in Fahrenheit?"
    print(f"\nQ: {q}\n")
    answer = run(q)
    print(f"\nA: {answer}\n")
