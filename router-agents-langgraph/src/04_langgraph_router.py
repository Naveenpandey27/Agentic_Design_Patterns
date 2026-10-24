"""
Example 4 — A router agent in LangGraph.

Here the router becomes a node in a graph. A router node writes the chosen
route into state; a conditional edge sends the query to the matching specialist
node; each specialist answers and the graph ends. This is the shape that scales
to real multi-agent systems.

    START -> router --(conditional edge on state["route"])--> weather -> END
                                                           -> math    -> END
                                                           -> general -> END

Run:
    python src/04_langgraph_router.py
"""
from typing import TypedDict

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

from router_schemas import RouteDecision, ROUTES
from tools import get_weather, calculator

load_dotenv()

router_llm = init_chat_model("openai:gpt-4o-mini").with_structured_output(RouteDecision)
llm = init_chat_model("openai:gpt-4o-mini")


class State(TypedDict):
    query: str
    route: str
    answer: str


def router_node(state: State) -> dict:
    """Decide the lane and record it in state."""
    decision = router_llm.invoke(
        f"Route this query into one of {ROUTES}. Query: {state['query']}"
    )
    print(f"  [router] -> {decision.route} (conf {decision.confidence:.2f})")
    return {"route": decision.route}


def weather_node(state: State) -> dict:
    # A real node could call the model with the tool bound; kept direct for clarity.
    city = state["query"].split()[-1].strip("?.")
    return {"answer": f"Weather: {get_weather.invoke({'city': city})}"}


def math_node(state: State) -> dict:
    ans = llm.invoke(
        f"Extract the arithmetic expression from this and reply with ONLY the "
        f"expression (digits and + - * / ( ) only): {state['query']}"
    ).content.strip()
    return {"answer": f"Result: {calculator.invoke({'expression': ans})}"}


def general_node(state: State) -> dict:
    return {"answer": llm.invoke(state["query"]).content}


def pick_lane(state: State) -> str:
    """Conditional-edge function: returns the next node name."""
    return state["route"]


builder = StateGraph(State)
builder.add_node("router", router_node)
builder.add_node("weather", weather_node)
builder.add_node("math", math_node)
builder.add_node("general", general_node)

builder.add_edge(START, "router")
builder.add_conditional_edges("router", pick_lane,
                              {"weather": "weather", "math": "math", "general": "general"})
for lane in ("weather", "math", "general"):
    builder.add_edge(lane, END)

graph = builder.compile()


if __name__ == "__main__":
    for q in ["What's the weather in Tokyo?",
              "What is 12 * (3 + 4)?",
              "Who painted the Mona Lisa?"]:
        print(f"\nQ: {q}")
        out = graph.invoke({"query": q})
        print(f"A: {out['answer']}")
