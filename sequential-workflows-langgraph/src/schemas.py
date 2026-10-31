"""
Structured types used across the pipeline.

Using Pydantic for the outline and the quality check means the model must return
clean, validated objects — no fragile text parsing between steps.
"""
from typing import List

from pydantic import BaseModel, Field


class Outline(BaseModel):
    """A blog-post outline produced by the planner step."""

    title: str = Field(description="A clear, engaging title for the post.")
    sections: List[str] = Field(
        description="3 to 5 short section headings, in order."
    )


class QualityCheck(BaseModel):
    """A validation verdict produced between steps."""

    passed: bool = Field(description="True if the draft meets the quality bar.")
    score: float = Field(ge=0.0, le=1.0, description="Overall quality score, 0 to 1.")
    issues: List[str] = Field(
        default_factory=list,
        description="Specific problems to fix. Empty if the draft passed.",
    )
