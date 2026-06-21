"""Pure carbon footprint calculator — zero I/O, fully unit-testable without mocks.

This module contains only deterministic, side-effect-free functions.
No Google SDK imports, no network calls, no database access.
"""

from __future__ import annotations

from app.carbon.factors import (
    CONSUMPTION_FACTORS,
    DIET_FACTORS,
    GLOBAL_AVERAGE,
    HOME_ELECTRICITY_PER_KWH,
    HOME_GAS_PER_KWH,
    PARIS_TARGET,
    TRANSPORT_FACTORS,
)


def _calculate_transport(
    mode: str,
    distance_km: float,
    trips_per_year: int,
) -> float:
    """Calculate annual transport emissions in kg CO₂e."""
    transport = TRANSPORT_FACTORS.get(mode)
    if transport is None:
        return 0.0
    if transport.unit == "kg/flight":
        return transport.factor * trips_per_year
    return transport.factor * distance_km * trips_per_year


def _calculate_home(
    electricity_kwh_monthly: float,
    gas_kwh_monthly: float,
) -> float:
    """Calculate annual home energy emissions in kg CO₂e."""
    annual_electricity = electricity_kwh_monthly * 12 * HOME_ELECTRICITY_PER_KWH
    annual_gas = gas_kwh_monthly * 12 * HOME_GAS_PER_KWH
    return annual_electricity + annual_gas


def _calculate_diet(diet_type: str) -> float:
    """Return annual diet emissions in kg CO₂e."""
    return DIET_FACTORS.get(diet_type, DIET_FACTORS["meat_medium"])


def _calculate_consumption(level: str) -> float:
    """Return annual consumption emissions in kg CO₂e."""
    return CONSUMPTION_FACTORS.get(level, CONSUMPTION_FACTORS["medium"])


def calculate_footprint(inputs: dict[str, object]) -> dict[str, object]:
    """Calculate a complete carbon footprint from user inputs.

    Parameters
    ----------
    inputs:
        Dictionary with keys matching ``CarbonInput`` model fields.

    Returns
    -------
    dict with:
        total_kg, breakdown (transport/home/diet/consumption),
        vs_global_average_pct, vs_paris_target_pct, ranked_categories.
    """
    transport_kg = _calculate_transport(
        mode=str(inputs.get("transport_mode", "car_petrol")),
        distance_km=float(inputs.get("distance_km", 0)),
        trips_per_year=int(inputs.get("trips_per_year", 0)),
    )
    home_kg = _calculate_home(
        electricity_kwh_monthly=float(inputs.get("electricity_kwh", 0)),
        gas_kwh_monthly=float(inputs.get("gas_kwh", 0)),
    )
    diet_kg = _calculate_diet(str(inputs.get("diet_type", "meat_medium")))
    consumption_kg = _calculate_consumption(str(inputs.get("consumption_level", "medium")))

    total_kg = round(transport_kg + home_kg + diet_kg + consumption_kg, 2)

    breakdown: dict[str, float] = {
        "transport": round(transport_kg, 2),
        "home": round(home_kg, 2),
        "diet": round(diet_kg, 2),
        "consumption": round(consumption_kg, 2),
    }

    vs_global = (
        round(((total_kg - GLOBAL_AVERAGE) / GLOBAL_AVERAGE) * 100, 1) if GLOBAL_AVERAGE else 0.0
    )
    vs_paris = round(((total_kg - PARIS_TARGET) / PARIS_TARGET) * 100, 1) if PARIS_TARGET else 0.0

    ranked = sorted(breakdown.items(), key=lambda item: item[1], reverse=True)
    ranked_categories = [{"category": cat, "kg": kg} for cat, kg in ranked]

    return {
        "total_kg": total_kg,
        "breakdown": breakdown,
        "vs_global_average_pct": vs_global,
        "vs_paris_target_pct": vs_paris,
        "ranked_categories": ranked_categories,
    }


# ---------------------------------------------------------------------------
# Rule-based fallback insights (used when Gemini is unavailable)
# ---------------------------------------------------------------------------

_CATEGORY_TIPS: dict[str, list[str]] = {
    "transport": [
        "Consider switching to public transport or cycling for short trips — you could cut transport emissions by up to 75%.",
        "Carpooling with just one other person halves your per-trip transport footprint.",
        "If you fly frequently, one fewer long-haul flight per year saves roughly 1.6 tonnes of CO₂.",
    ],
    "home": [
        "Switching to a 100% renewable electricity tariff can reduce home energy emissions by up to 80%.",
        "Improving home insulation typically cuts heating bills — and emissions — by 25-40%.",
        "Smart thermostats can reduce heating energy use by 10-15% with no comfort loss.",
    ],
    "diet": [
        "Replacing beef with chicken or plant protein just twice a week can cut diet emissions by 20%.",
        "Seasonal, locally-grown produce reduces food-miles and associated transport emissions.",
        "Reducing food waste by meal-planning can save both money and roughly 300 kg CO₂e per year.",
    ],
    "consumption": [
        "Buying fewer, higher-quality items that last longer significantly reduces your consumption footprint.",
        "Second-hand shopping for clothing can reduce fashion-related emissions by up to 80% per item.",
        "Repairing electronics instead of replacing them avoids the high carbon cost of manufacturing.",
    ],
}


def get_rule_based_insights(
    ranked_categories: list[dict[str, object]],
    breakdown: dict[str, float],
) -> list[dict[str, str]]:
    """Return exactly 3 deterministic insights based on the highest-emission categories.

    This is the offline fallback when the Gemini API is unavailable.
    Each insight includes a category label, a concrete tip, and a severity indicator.
    """
    insights: list[dict[str, str]] = []
    seen_categories: set[str] = set()

    for entry in ranked_categories:
        if len(insights) >= 3:
            break
        category = str(entry["category"])
        if category in seen_categories:
            continue
        seen_categories.add(category)

        tips = _CATEGORY_TIPS.get(category, [])
        if not tips:
            continue

        kg = breakdown.get(category, 0.0)
        if kg > 3000:
            severity = "high"
        elif kg > 1500:
            severity = "medium"
        else:
            severity = "low"

        tip_index = min(len(tips) - 1, max(0, {"high": 0, "medium": 1, "low": 2}.get(severity, 0)))
        insights.append(
            {
                "category": category,
                "tip": tips[tip_index],
                "severity": severity,
            }
        )

    # Guarantee exactly 3 insights even with sparse data
    fallback_tips = [
        {
            "category": "general",
            "tip": "Track your footprint monthly to identify trends and celebrate improvements.",
            "severity": "low",
        },
        {
            "category": "general",
            "tip": "Share your carbon journey with friends — collective action amplifies individual effort.",
            "severity": "low",
        },
        {
            "category": "general",
            "tip": "Consider carbon offsets for emissions you cannot yet eliminate.",
            "severity": "low",
        },
    ]
    while len(insights) < 3:
        insights.append(fallback_tips[len(insights) - len(insights)])  # always first fallback

    return insights[:3]
