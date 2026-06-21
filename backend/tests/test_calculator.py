"""Tests for the pure carbon calculator — zero mocking needed.

These tests verify the deterministic calculation logic and rule-based
insights without any I/O or external dependencies.
"""

from __future__ import annotations

from app.carbon.calculator import calculate_footprint, get_rule_based_insights
from app.carbon.factors import (
    CONSUMPTION_FACTORS,
    DIET_FACTORS,
    GLOBAL_AVERAGE,
    HOME_ELECTRICITY_PER_KWH,
    HOME_GAS_PER_KWH,
    PARIS_TARGET,
    TRANSPORT_FACTORS,
)


class TestCalculateFootprint:
    """Tests for the main calculate_footprint function."""

    def test_basic_calculation_returns_all_fields(self) -> None:
        """Result should contain all required keys."""
        inputs = {
            "transport_mode": "car_petrol",
            "distance_km": 20.0,
            "trips_per_year": 200,
            "electricity_kwh": 300.0,
            "gas_kwh": 100.0,
            "diet_type": "meat_medium",
            "consumption_level": "medium",
        }
        result = calculate_footprint(inputs)
        assert "total_kg" in result
        assert "breakdown" in result
        assert "vs_global_average_pct" in result
        assert "vs_paris_target_pct" in result
        assert "ranked_categories" in result

    def test_transport_car_petrol(self) -> None:
        """Petrol car transport calculation matches expected factor."""
        inputs = {
            "transport_mode": "car_petrol",
            "distance_km": 100.0,
            "trips_per_year": 1,
            "electricity_kwh": 0,
            "gas_kwh": 0,
            "diet_type": "vegan",
            "consumption_level": "low",
        }
        result = calculate_footprint(inputs)
        expected_transport = TRANSPORT_FACTORS["car_petrol"].factor * 100.0 * 1
        assert result["breakdown"]["transport"] == round(expected_transport, 2)

    def test_flight_short_haul_per_trip(self) -> None:
        """Short-haul flight factor is per-flight, not per-km."""
        inputs = {
            "transport_mode": "flight_short_haul",
            "distance_km": 999.0,  # Should be ignored for flights
            "trips_per_year": 2,
            "electricity_kwh": 0,
            "gas_kwh": 0,
            "diet_type": "vegan",
            "consumption_level": "low",
        }
        result = calculate_footprint(inputs)
        expected = TRANSPORT_FACTORS["flight_short_haul"].factor * 2
        assert result["breakdown"]["transport"] == round(expected, 2)

    def test_home_energy_annual(self) -> None:
        """Home energy is correctly annualized (monthly × 12)."""
        inputs = {
            "transport_mode": "train",
            "distance_km": 0,
            "trips_per_year": 0,
            "electricity_kwh": 100.0,
            "gas_kwh": 50.0,
            "diet_type": "vegan",
            "consumption_level": "low",
        }
        result = calculate_footprint(inputs)
        expected = (100.0 * 12 * HOME_ELECTRICITY_PER_KWH) + (50.0 * 12 * HOME_GAS_PER_KWH)
        assert result["breakdown"]["home"] == round(expected, 2)

    def test_diet_types(self) -> None:
        """Each diet type produces the correct annual emission."""
        for diet_type, expected_kg in DIET_FACTORS.items():
            inputs = {
                "transport_mode": "bus",
                "distance_km": 0,
                "trips_per_year": 0,
                "electricity_kwh": 0,
                "gas_kwh": 0,
                "diet_type": diet_type,
                "consumption_level": "low",
            }
            result = calculate_footprint(inputs)
            assert result["breakdown"]["diet"] == expected_kg

    def test_consumption_levels(self) -> None:
        """Each consumption level produces the correct annual emission."""
        for level, expected_kg in CONSUMPTION_FACTORS.items():
            inputs = {
                "transport_mode": "bus",
                "distance_km": 0,
                "trips_per_year": 0,
                "electricity_kwh": 0,
                "gas_kwh": 0,
                "diet_type": "vegan",
                "consumption_level": level,
            }
            result = calculate_footprint(inputs)
            assert result["breakdown"]["consumption"] == expected_kg

    def test_total_is_sum_of_categories(self) -> None:
        """Total kg must equal the sum of all breakdown categories."""
        inputs = {
            "transport_mode": "car_diesel",
            "distance_km": 50.0,
            "trips_per_year": 100,
            "electricity_kwh": 200.0,
            "gas_kwh": 150.0,
            "diet_type": "vegetarian",
            "consumption_level": "high",
        }
        result = calculate_footprint(inputs)
        breakdown = result["breakdown"]
        expected_total = sum(breakdown.values())
        assert abs(result["total_kg"] - expected_total) < 0.1

    def test_vs_global_average_pct(self) -> None:
        """Percentage vs global average is correctly calculated."""
        inputs = {
            "transport_mode": "bus",
            "distance_km": 0,
            "trips_per_year": 0,
            "electricity_kwh": 0,
            "gas_kwh": 0,
            "diet_type": "vegan",
            "consumption_level": "low",
        }
        result = calculate_footprint(inputs)
        total = result["total_kg"]
        expected_pct = round(((total - GLOBAL_AVERAGE) / GLOBAL_AVERAGE) * 100, 1)
        assert result["vs_global_average_pct"] == expected_pct

    def test_vs_paris_target_pct(self) -> None:
        """Percentage vs Paris target is correctly calculated."""
        inputs = {
            "transport_mode": "bus",
            "distance_km": 0,
            "trips_per_year": 0,
            "electricity_kwh": 0,
            "gas_kwh": 0,
            "diet_type": "vegan",
            "consumption_level": "low",
        }
        result = calculate_footprint(inputs)
        total = result["total_kg"]
        expected_pct = round(((total - PARIS_TARGET) / PARIS_TARGET) * 100, 1)
        assert result["vs_paris_target_pct"] == expected_pct

    def test_ranked_categories_sorted_descending(self) -> None:
        """Ranked categories are sorted highest-emission first."""
        inputs = {
            "transport_mode": "flight_long_haul",
            "distance_km": 0,
            "trips_per_year": 5,
            "electricity_kwh": 100.0,
            "gas_kwh": 50.0,
            "diet_type": "meat_heavy",
            "consumption_level": "high",
        }
        result = calculate_footprint(inputs)
        ranked = result["ranked_categories"]
        values = [r["kg"] for r in ranked]
        assert values == sorted(values, reverse=True)

    def test_zero_inputs_returns_diet_and_consumption(self) -> None:
        """With all-zero transport/home, total still includes diet + consumption."""
        inputs = {
            "transport_mode": "car_petrol",
            "distance_km": 0,
            "trips_per_year": 0,
            "electricity_kwh": 0,
            "gas_kwh": 0,
            "diet_type": "vegan",
            "consumption_level": "low",
        }
        result = calculate_footprint(inputs)
        assert result["total_kg"] > 0
        assert result["breakdown"]["transport"] == 0
        assert result["breakdown"]["home"] == 0


class TestRuleBasedInsights:
    """Tests for the deterministic fallback insights."""

    def test_returns_exactly_three(self) -> None:
        """Must always return exactly 3 insights."""
        ranked = [
            {"category": "transport", "kg": 5000.0},
            {"category": "diet", "kg": 3000.0},
            {"category": "home", "kg": 1000.0},
            {"category": "consumption", "kg": 500.0},
        ]
        breakdown = {"transport": 5000.0, "diet": 3000.0, "home": 1000.0, "consumption": 500.0}
        insights = get_rule_based_insights(ranked, breakdown)
        assert len(insights) == 3

    def test_insights_have_required_keys(self) -> None:
        """Each insight must have category, tip, and severity."""
        ranked = [{"category": "diet", "kg": 3300.0}]
        breakdown = {"diet": 3300.0}
        insights = get_rule_based_insights(ranked, breakdown)
        for insight in insights:
            assert "category" in insight
            assert "tip" in insight
            assert "severity" in insight

    def test_severity_levels(self) -> None:
        """Severity should be 'high' for emissions > 3000 kg."""
        ranked = [{"category": "transport", "kg": 5000.0}]
        breakdown = {"transport": 5000.0}
        insights = get_rule_based_insights(ranked, breakdown)
        assert insights[0]["severity"] == "high"

    def test_fallback_for_empty_categories(self) -> None:
        """Even with no ranked categories, returns 3 general insights."""
        insights = get_rule_based_insights([], {})
        assert len(insights) == 3
        for insight in insights:
            assert insight["category"] == "general"

    def test_no_duplicate_categories(self) -> None:
        """Should not return insights for the same category twice."""
        ranked = [
            {"category": "transport", "kg": 5000.0},
            {"category": "transport", "kg": 4000.0},
            {"category": "diet", "kg": 2000.0},
            {"category": "home", "kg": 1000.0},
        ]
        breakdown = {"transport": 5000.0, "diet": 2000.0, "home": 1000.0}
        insights = get_rule_based_insights(ranked, breakdown)
        non_general = [i for i in insights if i["category"] != "general"]
        categories = [i["category"] for i in non_general]
        assert len(categories) == len(set(categories))

    def test_unknown_category_skipped(self) -> None:
        """Unrecognized categories should be skipped in rule-based insights."""
        ranked = [{"category": "unknown_category", "kg": 5000.0}]
        breakdown = {"unknown_category": 5000.0}
        insights = get_rule_based_insights(ranked, breakdown)
        # Should skip "unknown_category" and fallback to general insights
        assert len(insights) == 3
        for insight in insights:
            assert insight["category"] == "general"


def test_invalid_transport_mode_returns_zero() -> None:
    """Invalid transport mode should bypass factors dict and return 0.0."""
    inputs = {
        "transport_mode": "invalid_mode",  # type: ignore[dict-item]
        "distance_km": 100.0,
        "trips_per_year": 10,
        "electricity_kwh": 0,
        "gas_kwh": 0,
        "diet_type": "vegan",
        "consumption_level": "low",
    }
    result = calculate_footprint(inputs)
    assert result["breakdown"]["transport"] == 0.0
