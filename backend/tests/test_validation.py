"""Tests for Pydantic model validation.

Every field constraint is tested at the boundary (exactly at ge/le) and
just beyond it, verifying that validation correctly accepts/rejects inputs.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.carbon import CarbonInput


class TestDeviceIdValidation:
    """Tests for device_id regex and length constraints."""

    def test_valid_alphanumeric_id(self) -> None:
        """Simple alphanumeric device_id should be accepted."""
        data = CarbonInput(device_id="abc123")
        assert data.device_id == "abc123"

    def test_valid_id_with_hyphens(self) -> None:
        """Hyphens are allowed in device_id."""
        data = CarbonInput(device_id="device-001-test")
        assert data.device_id == "device-001-test"

    def test_empty_id_rejected(self) -> None:
        """Empty device_id should be rejected (min_length=1)."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="")

    def test_too_long_id_rejected(self) -> None:
        """device_id longer than 64 chars should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="a" * 65)

    def test_exactly_64_chars_accepted(self) -> None:
        """device_id of exactly 64 chars should be accepted (boundary)."""
        data = CarbonInput(device_id="a" * 64)
        assert len(data.device_id) == 64

    def test_special_chars_rejected(self) -> None:
        """Special characters (not alphanumeric/hyphen) should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="device@user")

    def test_spaces_rejected(self) -> None:
        """Spaces should be rejected by the regex pattern."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="device 001")

    def test_underscores_rejected(self) -> None:
        """Underscores are not in the allowed pattern."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="device_001")


class TestNumericConstraints:
    """Tests for ge/le constraints on numeric fields."""

    def test_distance_km_zero_accepted(self) -> None:
        """distance_km=0 should be accepted (ge=0 boundary)."""
        data = CarbonInput(device_id="test", distance_km=0)
        assert data.distance_km == 0

    def test_distance_km_max_accepted(self) -> None:
        """distance_km=100000 should be accepted (le=100000 boundary)."""
        data = CarbonInput(device_id="test", distance_km=100000)
        assert data.distance_km == 100000

    def test_distance_km_over_max_rejected(self) -> None:
        """distance_km=100001 should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="test", distance_km=100001)

    def test_distance_km_negative_rejected(self) -> None:
        """Negative distance_km should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="test", distance_km=-1)

    def test_trips_per_year_zero_accepted(self) -> None:
        """trips_per_year=0 should be accepted (ge=0 boundary)."""
        data = CarbonInput(device_id="test", trips_per_year=0)
        assert data.trips_per_year == 0

    def test_trips_per_year_max_accepted(self) -> None:
        """trips_per_year=1000 should be accepted (le=1000 boundary)."""
        data = CarbonInput(device_id="test", trips_per_year=1000)
        assert data.trips_per_year == 1000

    def test_trips_per_year_over_max_rejected(self) -> None:
        """trips_per_year=1001 should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="test", trips_per_year=1001)

    def test_electricity_kwh_max_accepted(self) -> None:
        """electricity_kwh=10000 should be accepted (le=10000 boundary)."""
        data = CarbonInput(device_id="test", electricity_kwh=10000)
        assert data.electricity_kwh == 10000

    def test_electricity_kwh_over_max_rejected(self) -> None:
        """electricity_kwh=10001 should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="test", electricity_kwh=10001)

    def test_gas_kwh_max_accepted(self) -> None:
        """gas_kwh=10000 should be accepted (le=10000 boundary)."""
        data = CarbonInput(device_id="test", gas_kwh=10000)
        assert data.gas_kwh == 10000

    def test_gas_kwh_over_max_rejected(self) -> None:
        """gas_kwh=10001 should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="test", gas_kwh=10001)


class TestEnumConstraints:
    """Tests for Literal type constraints."""

    def test_valid_transport_modes(self) -> None:
        """All valid transport modes should be accepted."""
        modes = [
            "car_petrol",
            "car_diesel",
            "car_electric",
            "bus",
            "train",
            "flight_short_haul",
            "flight_long_haul",
        ]
        for mode in modes:
            data = CarbonInput(device_id="test", transport_mode=mode)
            assert data.transport_mode == mode

    def test_invalid_transport_mode_rejected(self) -> None:
        """Invalid transport mode should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="test", transport_mode="skateboard")  # type: ignore[arg-type]

    def test_valid_diet_types(self) -> None:
        """All valid diet types should be accepted."""
        for diet in ["meat_heavy", "meat_medium", "vegetarian", "vegan"]:
            data = CarbonInput(device_id="test", diet_type=diet)
            assert data.diet_type == diet

    def test_invalid_diet_rejected(self) -> None:
        """Invalid diet type should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="test", diet_type="fruitarian")  # type: ignore[arg-type]

    def test_valid_consumption_levels(self) -> None:
        """All valid consumption levels should be accepted."""
        for level in ["high", "medium", "low"]:
            data = CarbonInput(device_id="test", consumption_level=level)
            assert data.consumption_level == level

    def test_invalid_consumption_rejected(self) -> None:
        """Invalid consumption level should be rejected."""
        with pytest.raises(ValidationError):
            CarbonInput(device_id="test", consumption_level="extreme")  # type: ignore[arg-type]
