"""Carbon emission factors with cited sources.

Every constant includes an inline citation to its primary data source.
All values are in kilograms of CO₂-equivalent unless otherwise noted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

# ---------------------------------------------------------------------------
# Transport factors (kg CO₂e per km, except flights which are per flight)
# ---------------------------------------------------------------------------
TRANSPORT_CAR_PETROL: Final[float] = 0.170  # DEFRA 2023 — average petrol car
TRANSPORT_CAR_DIESEL: Final[float] = 0.161  # DEFRA 2023 — average diesel car
TRANSPORT_CAR_ELECTRIC: Final[float] = 0.053  # DEFRA 2023 — battery EV, UK grid mix
TRANSPORT_BUS: Final[float] = 0.089  # DEFRA 2023 — average local bus
TRANSPORT_TRAIN: Final[float] = 0.041  # DEFRA 2023 — national rail average
TRANSPORT_FLIGHT_SHORT_HAUL: Final[float] = 255.0  # ICAO Carbon Calculator — <3 h flight
TRANSPORT_FLIGHT_LONG_HAUL: Final[float] = 1620.0  # ICAO Carbon Calculator — >6 h flight

# ---------------------------------------------------------------------------
# Home energy factors (kg CO₂e per kWh)
# ---------------------------------------------------------------------------
HOME_ELECTRICITY_PER_KWH: Final[float] = 0.233  # US EPA eGRID 2023 — national average
HOME_GAS_PER_KWH: Final[float] = 0.203  # DEFRA 2023 — natural gas

# ---------------------------------------------------------------------------
# Diet factors (kg CO₂e per year)
# ---------------------------------------------------------------------------
DIET_MEAT_HEAVY: Final[float] = 3300.0  # Our World in Data — high-meat diet
DIET_MEAT_MEDIUM: Final[float] = 2500.0  # Our World in Data — moderate meat
DIET_VEGETARIAN: Final[float] = 1700.0  # Our World in Data — lacto-ovo vegetarian
DIET_VEGAN: Final[float] = 1100.0  # Our World in Data — fully plant-based

# ---------------------------------------------------------------------------
# Consumption / lifestyle factors (kg CO₂e per year)
# ---------------------------------------------------------------------------
CONSUMPTION_HIGH: Final[float] = 4000.0  # IPCC AR6 — high-consumption lifestyle
CONSUMPTION_MEDIUM: Final[float] = 2500.0  # IPCC AR6 — moderate consumption
CONSUMPTION_LOW: Final[float] = 1200.0  # IPCC AR6 — low-consumption lifestyle

# ---------------------------------------------------------------------------
# Reference benchmarks (kg CO₂e per year)
# ---------------------------------------------------------------------------
GLOBAL_AVERAGE: Final[float] = 4000.0  # World Bank 2023 — global per-capita mean
PARIS_TARGET: Final[float] = 2000.0  # Paris Agreement — 2030 per-capita goal


# ---------------------------------------------------------------------------
# Lookup dictionaries for runtime resolution
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TransportMode:
    """Immutable descriptor for a transport emission mode."""

    factor: float
    unit: str
    label: str


TRANSPORT_FACTORS: Final[dict[str, TransportMode]] = {
    "car_petrol": TransportMode(TRANSPORT_CAR_PETROL, "kg/km", "Petrol car"),
    "car_diesel": TransportMode(TRANSPORT_CAR_DIESEL, "kg/km", "Diesel car"),
    "car_electric": TransportMode(TRANSPORT_CAR_ELECTRIC, "kg/km", "Electric car"),
    "bus": TransportMode(TRANSPORT_BUS, "kg/km", "Bus"),
    "train": TransportMode(TRANSPORT_TRAIN, "kg/km", "Train"),
    "flight_short_haul": TransportMode(
        TRANSPORT_FLIGHT_SHORT_HAUL, "kg/flight", "Short-haul flight"
    ),
    "flight_long_haul": TransportMode(TRANSPORT_FLIGHT_LONG_HAUL, "kg/flight", "Long-haul flight"),
}

DIET_FACTORS: Final[dict[str, float]] = {
    "meat_heavy": DIET_MEAT_HEAVY,
    "meat_medium": DIET_MEAT_MEDIUM,
    "vegetarian": DIET_VEGETARIAN,
    "vegan": DIET_VEGAN,
}

CONSUMPTION_FACTORS: Final[dict[str, float]] = {
    "high": CONSUMPTION_HIGH,
    "medium": CONSUMPTION_MEDIUM,
    "low": CONSUMPTION_LOW,
}
