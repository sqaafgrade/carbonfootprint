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

    async def test_health_with_x_forwarded_for(self, client: AsyncClient) -> None:
        """GET /api/health with X-Forwarded-For header should successfully return 200."""
        response = await client.get("/api/health", headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8"})
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCalculateRoute:
    """POST /api/calculate endpoint tests."""

    async def test_calculate_success(
        self,
        client: AsyncClient,
        valid_carbon_input: dict,  # type: ignore[type-arg]
    ) -> None:
        """Valid input should return 200 with complete result."""
        response = await client.post("/api/calculate", json=valid_carbon_input, headers={"X-Forwarded-For": "1.2.3.4, 5.6.7.8"})
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

    async def test_calculate_with_gemini_success(
        self,
        client: AsyncClient,
        valid_carbon_input: dict,
    ) -> None:
        """Should return insights with source 'gemini' when Gemini is enabled and succeeds."""
        from unittest.mock import AsyncMock, patch
        mock_insights = [
            {"category": "transport", "tip": "Ride a bike", "severity": "high"},
            {"category": "home", "tip": "Turn off lights", "severity": "low"},
            {"category": "diet", "tip": "Eat less meat", "severity": "medium"},
        ]
        with (
            patch("app.routes.calculate.get_settings") as mock_settings,
            patch("app.routes.calculate.get_gemini_insights", new_callable=AsyncMock) as mock_get_gemini,
        ):
            mock_settings.return_value.use_gemini = True
            mock_settings.return_value.rate_limit_per_minute = 100
            mock_get_gemini.return_value = mock_insights
            response = await client.post("/api/calculate", json=valid_carbon_input)
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "gemini"
            assert len(data["insights"]) == 3
            assert data["insights"][0]["tip"] == "Ride a bike"

    async def test_calculate_with_gemini_failure_fallback(
        self,
        client: AsyncClient,
        valid_carbon_input: dict,
    ) -> None:
        """Should fallback to rules when Gemini is enabled but fails."""
        from unittest.mock import AsyncMock, patch

        from app.services.gemini_service import GeminiUnavailableError
        with (
            patch("app.routes.calculate.get_settings") as mock_settings,
            patch("app.routes.calculate.get_gemini_insights", new_callable=AsyncMock) as mock_get_gemini,
        ):
            mock_settings.return_value.use_gemini = True
            mock_settings.return_value.rate_limit_per_minute = 100
            mock_get_gemini.side_effect = GeminiUnavailableError("Gemini is offline")
            response = await client.post("/api/calculate", json=valid_carbon_input)
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "rules"
            assert len(data["insights"]) == 3


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

    async def test_insights_with_gemini_success(
        self,
        client: AsyncClient,
        valid_carbon_input: dict,
    ) -> None:
        """Should return Gemini insights when enabled and succeeds."""
        from unittest.mock import AsyncMock, patch
        mock_insights = [
            {"category": "transport", "tip": "Ride a bike", "severity": "high"},
            {"category": "home", "tip": "Turn off lights", "severity": "low"},
            {"category": "diet", "tip": "Eat less meat", "severity": "medium"},
        ]
        with (
            patch("app.routes.insights.get_settings") as mock_settings,
            patch("app.routes.insights.get_gemini_insights", new_callable=AsyncMock) as mock_get_gemini,
        ):
            mock_settings.return_value.use_gemini = True
            mock_settings.return_value.rate_limit_per_minute = 100
            mock_get_gemini.return_value = mock_insights
            response = await client.post("/api/insights", json=valid_carbon_input)
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "gemini"
            assert len(data["insights"]) == 3
            assert data["insights"][0]["tip"] == "Ride a bike"

    async def test_insights_with_gemini_failure_fallback(
        self,
        client: AsyncClient,
        valid_carbon_input: dict,
    ) -> None:
        """Should fallback to rule-based insights when Gemini is enabled but fails."""
        from unittest.mock import AsyncMock, patch

        from app.services.gemini_service import GeminiUnavailableError
        with (
            patch("app.routes.insights.get_settings") as mock_settings,
            patch("app.routes.insights.get_gemini_insights", new_callable=AsyncMock) as mock_get_gemini,
        ):
            mock_settings.return_value.use_gemini = True
            mock_settings.return_value.rate_limit_per_minute = 100
            mock_get_gemini.side_effect = GeminiUnavailableError("Gemini is offline")
            response = await client.post("/api/insights", json=valid_carbon_input)
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "rules"
            assert len(data["insights"]) == 3


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


class TestSpaServing:
    """SPA and static files routing tests."""

    async def test_serve_spa_index_when_not_found(self, tmp_path) -> None:
        """Should fall back to index.html if the requested file does not exist."""
        from unittest.mock import patch

        from httpx import ASGITransport, AsyncClient

        from app.main import create_app

        # Create dummy index.html in tmp_path
        (tmp_path / "index.html").write_text("INDEX_HTML_CONTENT")
        (tmp_path / "assets").mkdir(parents=True, exist_ok=True)

        with patch("app.main.STATIC_DIR", tmp_path):
            test_app = create_app()
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # Request a non-existent file
                response = await client.get("/some-random-route")
                assert response.status_code == 200
                assert response.text == "INDEX_HTML_CONTENT"

    async def test_serve_spa_file_exists(self, tmp_path) -> None:
        """Should return the actual file if it exists in the static directory."""
        from unittest.mock import patch

        from httpx import ASGITransport, AsyncClient

        from app.main import create_app

        # Create dummy file in tmp_path
        (tmp_path / "test.txt").write_text("FILE_CONTENT")
        (tmp_path / "index.html").write_text("INDEX")
        (tmp_path / "assets").mkdir(parents=True, exist_ok=True)

        with patch("app.main.STATIC_DIR", tmp_path):
            test_app = create_app()
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/test.txt")
                assert response.status_code == 200
                assert response.text == "FILE_CONTENT"

    async def test_api_only_mode_if_dir_missing(self, tmp_path) -> None:
        """Should log warning and skip SPA mounting if static dir does not exist."""
        from unittest.mock import patch

        from app.main import create_app

        non_existent_path = tmp_path / "missing_dir"

        with patch("app.main.STATIC_DIR", non_existent_path):
            test_app = create_app()
            from httpx import ASGITransport, AsyncClient
            transport = ASGITransport(app=test_app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/some-random-route")
                assert response.status_code == 404

