"""
Shared types for routing.

ROUTES is the single source of truth for the lanes our router can pick.
RouteDecision is the structured object we ask the LLM to return — forcing the
model to give us a clean route + confidence + reasoning instead of free text
we have to parse by hand.
"""
from typing import Literal

from pydantic import BaseModel, Field

# The lanes the router can choose between. Keep this list and the specialists
# in agents.py in sync.
ROUTES = ("weather", "math", "general")
Route = Literal["weather", "math", "general"]


class RouteDecision(BaseModel):
    """A structured routing decision returned by the LLM router."""

    route: Route = Field(
        description="Which specialist should handle this query."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="How confident you are in this route, from 0.0 to 1.0.",
    )
    reasoning: str = Field(
        description="One short sentence explaining why you chose this route."
    )
