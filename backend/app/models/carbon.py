"""Pydantic v2 models for carbon footprint calculation.

Full field constraints (ge/le on all numerics), Literal types for enums,
regex-constrained device_id for safe identification.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

TransportMode = Literal[
    "car_petrol",
    "car_diesel",
    "car_electric",
    "bus",
    "train",
    "flight_short_haul",
    "flight_long_haul",
]

DietType = Literal["meat_heavy", "meat_medium", "vegetarian", "vegan"]

ConsumptionLevel = Literal["high", "medium", "low"]


class CarbonInput(BaseModel):
    """Validated input for a carbon footprint calculation.

    Every numeric field has explicit ge/le bounds. The ``device_id`` is
    regex-constrained to alphanumeric + hyphens only (max 64 chars).
    """

    device_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z0-9\-]+$",
        description="Anonymous device identifier (alphanumeric + hyphens only)",
    )

    # Transport
    transport_mode: TransportMode = Field(
        "car_petrol",
        description="Primary transport mode",
    )
    distance_km: float = Field(
        0.0,
        ge=0,
        le=100000,
        description="Weekly commute distance in km (0–100,000)",
    )
    trips_per_year: int = Field(
        0,
        ge=0,
        le=1000,
        description="Number of trips per year (0–1,000)",
    )

    # Home energy
    electricity_kwh: float = Field(
        0.0,
        ge=0,
        le=10000,
        description="Monthly electricity usage in kWh (0–10,000)",
    )
    gas_kwh: float = Field(
        0.0,
        ge=0,
        le=10000,
        description="Monthly gas usage in kWh (0–10,000)",
    )

    # Diet
    diet_type: DietType = Field(
        "meat_medium",
        description="Dietary pattern",
    )

    # Consumption
    consumption_level: ConsumptionLevel = Field(
        "medium",
        description="General consumption lifestyle level",
    )


class CategoryBreakdown(BaseModel):
    """Emission breakdown by category."""

    transport: float = Field(..., ge=0, description="Transport emissions in kg CO₂e")
    home: float = Field(..., ge=0, description="Home energy emissions in kg CO₂e")
    diet: float = Field(..., ge=0, description="Diet emissions in kg CO₂e")
    consumption: float = Field(..., ge=0, description="Consumption emissions in kg CO₂e")


class RankedCategory(BaseModel):
    """A category ranked by emission magnitude."""

    category: str = Field(..., description="Category name")
    kg: float = Field(..., ge=0, description="Emissions in kg CO₂e")


class CarbonResult(BaseModel):
    """Complete carbon footprint calculation result."""

    total_kg: float = Field(..., ge=0, description="Total annual emissions in kg CO₂e")
    breakdown: CategoryBreakdown = Field(..., description="Per-category breakdown")
    vs_global_average_pct: float = Field(
        ...,
        description="Percentage difference vs global average (negative = below average)",
    )
    vs_paris_target_pct: float = Field(
        ...,
        description="Percentage difference vs Paris Agreement target",
    )
    ranked_categories: list[RankedCategory] = Field(
        ...,
        description="Categories ranked by emission magnitude (highest first)",
    )
    insights: list[dict[str, str]] = Field(
        default_factory=list,
        description="Actionable reduction insights (AI or rule-based)",
    )
    source: Literal["gemini", "rules"] = Field(
        "rules",
        description="Whether insights came from Gemini AI or rule-based fallback",
    )
