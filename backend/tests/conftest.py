"""Shared test fixtures.

Uses the ``create_app()`` factory with settings overrides and mocked
Google Cloud clients so all tests run fully offline.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture()
def test_settings() -> Settings:
    """Create settings with all external services disabled."""
    return Settings(
        project_id="test-project",
        environment="development",
        use_gemini=False,
        use_firestore=False,
        use_bigquery=False,
        use_pubsub=False,
        rate_limit_per_minute=100,
        cors_origins="http://localhost:3000",
    )


@pytest.fixture()
def app(test_settings: Settings):  # type: ignore[no-untyped-def]
    """Create a fresh FastAPI app with test settings."""
    with (
        patch("app.core.config.get_settings", return_value=test_settings),
    ):
        application = create_app(settings=test_settings)
        yield application


@pytest.fixture()
async def client(app) -> AsyncGenerator[AsyncClient, None]:  # type: ignore[no-untyped-def, type-arg]
    """Async HTTP client for integration testing against the test app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
def valid_carbon_input() -> dict:  # type: ignore[type-arg]
    """Standard valid input for carbon calculation tests."""
    return {
        "device_id": "test-device-001",
        "transport_mode": "car_petrol",
        "distance_km": 30.0,
        "trips_per_year": 250,
        "electricity_kwh": 300.0,
        "gas_kwh": 200.0,
        "diet_type": "meat_medium",
        "consumption_level": "medium",
    }


@pytest.fixture()
def mock_firestore_client() -> MagicMock:
    """Mock Firestore client that tracks calls but never hits the network."""
    client = MagicMock()
    collection = MagicMock()
    collection.add = AsyncMock(return_value=(None, MagicMock(id="mock-doc-id")))
    collection.where.return_value.order_by.return_value.limit.return_value.stream = AsyncMock(
        return_value=[]
    )
    client.collection.return_value = collection
    return client


@pytest.fixture()
def mock_bigquery_client() -> MagicMock:
    """Mock BigQuery client that tracks calls but never hits the network."""
    client = MagicMock()
    client.insert_rows_json.return_value = []
    return client


@pytest.fixture()
def mock_pubsub_publisher() -> MagicMock:
    """Mock Pub/Sub publisher that tracks calls but never hits the network."""
    publisher = MagicMock()
    future = MagicMock()
    future.result.return_value = "mock-message-id"
    publisher.publish.return_value = future
    publisher.topic_path.return_value = "projects/test/topics/carbon-calculations"
    return publisher
