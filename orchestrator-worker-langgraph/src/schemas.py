"""
Structured types for the orchestrator-worker system.

The orchestrator returns a Plan (a list of Sections). Each Section is a self-
contained unit of work a single worker can handle. Using Pydantic here means the
orchestrator's decomposition is validated structure, not text we have to parse.
"""
from typing import List

from pydantic import BaseModel, Field


class Section(BaseModel):
    """One unit of work the orchestrator hands to a single worker."""

    name: str = Field(description="Short section heading.")
    brief: str = Field(description="One sentence telling the worker what to cover.")


class Plan(BaseModel):
    """The orchestrator's decomposition of a task into worker-sized sections."""

    sections: List[Section] = Field(
        description="3 to 5 sections that together cover the whole task."
    )
