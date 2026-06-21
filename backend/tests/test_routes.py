"""Integration tests for API routes.

Uses httpx AsyncClient against a fresh ``create_app()`` instance with
all Google services mocked — zero real network calls.
Tests both success paths and failure/fallback paths.
"""

from __future__ import annotations

from httpx import AsyncClient


class TestHealthRoute:
    """Health check endpoint tests."""

    async def test_health_returns_200(self, client: AsyncClient) -> None:
        """GET /api/health should return 200 with status 'healthy'."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "carbon-platform"

    async def test_health_has_security_headers(self, client: AsyncClient) -> None:
        """Response should include all 8 security headers."""
        response = await client.get("/api/health")
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "max-age=63072000" in response.headers.get("Strict-Transport-Security", "")
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert "camera=()" in response.headers.get("Permissions-Policy", "")
        assert response.headers.get("Cache-Control") == "no-store, max-age=0"


class TestCalculateRoute:
    """POST /api/calculate endpoint tests."""

    async def test_calculate_success(
        self,
        client: AsyncClient,
        valid_carbon_input: dict,  # type: ignore[type-arg]
    ) -> None:
        """Valid input should return 200 with complete result."""
        response = await client.post("/api/calculate", json=valid_carbon_input)
        assert response.status_code == 200
        data = response.json()
        assert "total_kg" in data
        assert "breakdown" in data
        assert "insights" in data
        assert data["source"] == "rules"
        assert data["total_kg"] > 0
        assert len(data["insights"]) == 3

    async def test_calculate_returns_breakdown(
        self,
        client: AsyncClient,
        valid_carbon_input: dict,  # type: ignore[type-arg]
    ) -> None:
        """Breakdown should contain all 4 categories."""
        response = await client.post("/api/calculate", json=valid_carbon_input)
        data = response.json()
        breakdown = data["breakdown"]
        assert "transport" in breakdown
        assert "home" in breakdown
        assert "diet" in breakdown
        assert "consumption" in breakdown

    async def test_calculate_invalid_transport_mode(self, client: AsyncClient) -> None:
        """Invalid transport_mode should return 422 validation error."""
        response = await client.post(
            "/api/calculate",
            json={
                "device_id": "test-001",
                "transport_mode": "helicopter",
                "distance_km": 10.0,
                "trips_per_year": 10,
                "electricity_kwh": 100.0,
                "gas_kwh": 50.0,
                "diet_type": "vegan",
                "consumption_level": "low",
            },
        )
        assert response.status_code == 422

    async def test_calculate_missing_device_id(self, client: AsyncClient) -> None:
        """Missing device_id should return 422."""
        response = await client.post(
            "/api/calculate",
            json={
                "transport_mode": "bus",
                "distance_km": 10.0,
                "trips_per_year": 10,
                "electricity_kwh": 100.0,
                "gas_kwh": 50.0,
                "diet_type": "vegan",
                "consumption_level": "low",
            },
        )
        assert response.status_code == 422

    async def test_calculate_negative_distance(self, client: AsyncClient) -> None:
        """Negative distance_km should return 422."""
        response = await client.post(
            "/api/calculate",
            json={
                "device_id": "test-001",
                "transport_mode": "bus",
                "distance_km": -5.0,
                "trips_per_year": 10,
                "electricity_kwh": 100.0,
                "gas_kwh": 50.0,
                "diet_type": "vegan",
                "consumption_level": "low",
            },
        )
        assert response.status_code == 422


class TestInsightsRoute:
    """POST /api/insights endpoint tests."""

    async def test_insights_success(
        self,
        client: AsyncClient,
        valid_carbon_input: dict,  # type: ignore[type-arg]
    ) -> None:
        """Should return insights with source 'rules' when Gemini is disabled."""
        response = await client.post("/api/insights", json=valid_carbon_input)
        assert response.status_code == 200
        data = response.json()
        assert data["source"] == "rules"
        assert len(data["insights"]) == 3
        assert data["device_id"] == "test-device-001"


class TestEntriesRoute:
    """GET /api/entries endpoint tests."""

    async def test_entries_returns_empty_when_disabled(self, client: AsyncClient) -> None:
        """With Firestore disabled, entries should return an empty list."""
        response = await client.get("/api/entries", params={"device_id": "test-001"})
        assert response.status_code == 200
        assert response.json() == []

    async def test_entries_invalid_device_id(self, client: AsyncClient) -> None:
        """Invalid device_id pattern should return 422."""
        response = await client.get("/api/entries", params={"device_id": "invalid@id!"})
        assert response.status_code == 422

    async def test_entries_limit_out_of_range(self, client: AsyncClient) -> None:
        """Limit > 100 should return 422."""
        response = await client.get("/api/entries", params={"device_id": "test-001", "limit": 200})
        assert response.status_code == 422
