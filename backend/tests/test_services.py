"""Tests for Google Cloud services — fire-and-forget guarantee.

Critical: bigquery_service and pubsub_service must NEVER raise,
even when the underlying client throws exceptions.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.services.bigquery_service import log_calculation_event
from app.services.pubsub_service import publish_calculation_event


class TestBigQueryServiceNeverRaises:
    """BigQuery service must never propagate exceptions."""

    async def test_logs_event_when_enabled(self) -> None:
        """Should call insert_rows_json when USE_BIGQUERY=true."""
        mock_client = MagicMock()
        mock_client.insert_rows_json.return_value = []

        with (
            patch("app.services.bigquery_service._get_client", return_value=mock_client),
            patch("app.services.bigquery_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.use_bigquery = True
            mock_settings.return_value.project_id = "test"
            mock_settings.return_value.bigquery_dataset = "test_dataset"
            mock_settings.return_value.bigquery_table = "test_table"

            await log_calculation_event(
                device_id="test-001",
                total_kg=5000.0,
                breakdown={
                    "transport": 2000.0,
                    "home": 1000.0,
                    "diet": 1500.0,
                    "consumption": 500.0,
                },
                source="rules",
            )
            mock_client.insert_rows_json.assert_called_once()

    async def test_does_not_raise_on_client_error(self) -> None:
        """Should catch and log exceptions, never raising."""
        mock_client = MagicMock()
        mock_client.insert_rows_json.side_effect = RuntimeError("BigQuery exploded")

        with (
            patch("app.services.bigquery_service._get_client", return_value=mock_client),
            patch("app.services.bigquery_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.use_bigquery = True
            mock_settings.return_value.project_id = "test"
            mock_settings.return_value.bigquery_dataset = "test_dataset"
            mock_settings.return_value.bigquery_table = "test_table"

            # This MUST NOT raise
            await log_calculation_event(
                device_id="test-001",
                total_kg=5000.0,
                breakdown={"transport": 2000.0},
                source="rules",
            )

    async def test_skips_when_disabled(self) -> None:
        """Should return immediately when USE_BIGQUERY=false."""
        with patch("app.services.bigquery_service.get_settings") as mock_settings:
            mock_settings.return_value.use_bigquery = False
            await log_calculation_event(
                device_id="test-001",
                total_kg=5000.0,
                breakdown={},
                source="rules",
            )


class TestPubSubServiceNeverRaises:
    """Pub/Sub service must never propagate exceptions."""

    async def test_publishes_event_when_enabled(self) -> None:
        """Should call publish when USE_PUBSUB=true."""
        mock_publisher = MagicMock()
        future = MagicMock()
        future.result.return_value = "msg-001"
        mock_publisher.publish.return_value = future
        mock_publisher.topic_path.return_value = "projects/test/topics/test"

        with (
            patch("app.services.pubsub_service._get_publisher", return_value=mock_publisher),
            patch("app.services.pubsub_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.use_pubsub = True
            mock_settings.return_value.project_id = "test"
            mock_settings.return_value.pubsub_topic = "test-topic"

            await publish_calculation_event(
                device_id="test-001",
                total_kg=5000.0,
                breakdown={"transport": 2000.0},
            )
            mock_publisher.publish.assert_called_once()

    async def test_does_not_raise_on_publish_error(self) -> None:
        """Should catch and log exceptions, never raising."""
        mock_publisher = MagicMock()
        mock_publisher.publish.side_effect = RuntimeError("Pub/Sub exploded")
        mock_publisher.topic_path.return_value = "projects/test/topics/test"

        with (
            patch("app.services.pubsub_service._get_publisher", return_value=mock_publisher),
            patch("app.services.pubsub_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.use_pubsub = True
            mock_settings.return_value.project_id = "test"
            mock_settings.return_value.pubsub_topic = "test-topic"

            # This MUST NOT raise
            await publish_calculation_event(
                device_id="test-001",
                total_kg=5000.0,
                breakdown={"transport": 2000.0},
            )

    async def test_skips_when_disabled(self) -> None:
        """Should return immediately when USE_PUBSUB=false."""
        with patch("app.services.pubsub_service.get_settings") as mock_settings:
            mock_settings.return_value.use_pubsub = False
            await publish_calculation_event(
                device_id="test-001",
                total_kg=5000.0,
                breakdown={},
            )
