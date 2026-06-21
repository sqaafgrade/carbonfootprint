"""Pydantic v2 models for AI-generated insights."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Insight(BaseModel):
    """A single actionable insight for carbon reduction."""

    category: str = Field(..., description="Emission category this insight targets")
    tip: str = Field(..., min_length=10, max_length=500, description="Actionable reduction tip")
    severity: str = Field(
        ...,
        pattern=r"^(high|medium|low)$",
        description="Impact severity level",
    )


class InsightsResponse(BaseModel):
    """Response wrapper for a list of insights."""

    insights: list[Insight] = Field(..., description="List of actionable insights")
    source: str = Field(
        ...,
        pattern=r"^(gemini|rules)$",
        description="Source of the insights",
    )
    device_id: str = Field(..., description="Device that requested insights")
