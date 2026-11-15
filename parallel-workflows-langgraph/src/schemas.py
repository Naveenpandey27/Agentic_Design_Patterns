"""
Structured types for the parallel research system.

SubReport is what each parallel researcher returns. Using a reducer on a list of
these (see state.py) lets many researchers write their results concurrently
without clobbering each other.
"""
from typing import List

from pydantic import BaseModel, Field


class SubReport(BaseModel):
    """One researcher's finding on a single subtopic."""

    subtopic: str = Field(description="The subtopic this report covers.")
    summary: str = Field(description="A concise 2-3 sentence summary of findings.")
    key_points: List[str] = Field(description="2-4 bullet-point takeaways.")
