"""
Example 2 — The ReAct loop as a LangGraph graph.

Same cycle as example 1, but built with LangGraph's StateGraph. Two nodes
(agent + tools) and a conditional edge recreate Reason -> Act -> Observe,
with the message history managed for you.

Run:
    python src/02_langgraph_react.py
"""
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from tools import get_weather, c_to_fahrenheit

load_dotenv()

TOOLS = [get_weather, c_to_fahrenheit]
llm_with_tools = init_chat_model("openai:gpt-4o-mini").bind_tools(TOOLS)


def agent(state: MessagesState) -> dict:
    """The REASON node: call the model with the conversation so far."""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build the graph: START -> agent -> (tools -> agent)* -> END
builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(TOOLS))        # the ACT + OBSERVE node
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)  # tool call? -> tools, else -> END
builder.add_edge("tools", "agent")                # loop the observation back in
graph = builder.compile()


if __name__ == "__main__":
    q = "What's the weather in Delhi, and what is that temperature in Fahrenheit?"
    print(f"\nQ: {q}\n")
    result = graph.invoke({"messages": [HumanMessage(q)]})

    # Print the full trace so you can watch the loop happen.
    for m in result["messages"]:
        m.pretty_print()
