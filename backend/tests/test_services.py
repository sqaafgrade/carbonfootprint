"""Tests for Google Cloud services — fire-and-forget guarantee.

Critical: bigquery_service and pubsub_service must NEVER raise,
even when the underlying client throws exceptions.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

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


class TestFirestoreServiceNeverRaises:
    """Firestore service must never propagate exceptions and handle disabled states."""

    async def test_save_entry_disabled(self) -> None:
        """Should skip saving if Firestore is disabled."""
        from app.services.firestore_service import save_entry

        with patch("app.services.firestore_service.get_settings") as mock_settings:
            mock_settings.return_value.use_firestore = False
            result = await save_entry("test-001", {"total_kg": 50.0})
            assert result is None

    async def test_save_entry_success(self) -> None:
        """Should return document ID on successful save."""
        from app.services.firestore_service import save_entry

        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_ref = MagicMock()
        mock_ref.id = "mock-doc-id"
        mock_collection.add = AsyncMock(return_value=(None, mock_ref))
        mock_client.collection.return_value = mock_collection

        with (
            patch("app.services.firestore_service._get_client", return_value=mock_client),
            patch("app.services.firestore_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.use_firestore = True
            mock_settings.return_value.firestore_collection = "test_collection"

            result = await save_entry("device-123", {"total_kg": 120.5, "source": "gemini"})
            assert result == "mock-doc-id"
            mock_collection.add.assert_called_once()

    async def test_save_entry_exception_caught(self) -> None:
        """Should log warning and return None on save failure."""
        from app.services.firestore_service import save_entry

        mock_client = MagicMock()
        mock_client.collection.side_effect = RuntimeError("Firestore connection lost")

        with (
            patch("app.services.firestore_service._get_client", return_value=mock_client),
            patch("app.services.firestore_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.use_firestore = True
            mock_settings.return_value.firestore_collection = "test_collection"

            result = await save_entry("device-123", {"total_kg": 120.5})
            assert result is None

    async def test_get_entries_disabled(self) -> None:
        """Should return empty list if Firestore is disabled."""
        from app.services.firestore_service import get_entries

        with patch("app.services.firestore_service.get_settings") as mock_settings:
            mock_settings.return_value.use_firestore = False
            result = await get_entries("test-001")
            assert result == []

    async def test_get_entries_success(self) -> None:
        """Should stream documents and convert timestamps to ISO strings."""
        from datetime import UTC, datetime

        from app.services.firestore_service import get_entries

        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_query = MagicMock()
        mock_client.collection.return_value = mock_collection
        mock_collection.where.return_value.order_by.return_value.limit.return_value = mock_query

        # Mock query.stream() async generator
        class AsyncMockIterator:
            def __init__(self, items):
                self.items = items
                self.index = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.index >= len(self.items):
                    raise StopAsyncIteration
                item = self.items[self.index]
                self.index += 1
                return item

        mock_doc = MagicMock()
        mock_doc.id = "doc-id-1"
        mock_doc.to_dict.return_value = {
            "device_id": "test-001",
            "total_kg": 500.0,
            "created_at": datetime(2026, 6, 21, 12, 0, 0, tzinfo=UTC),
        }
        mock_query.stream.return_value = AsyncMockIterator([mock_doc])

        with (
            patch("app.services.firestore_service._get_client", return_value=mock_client),
            patch("app.services.firestore_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.use_firestore = True
            mock_settings.return_value.firestore_collection = "test_collection"

            entries = await get_entries("test-001")
            assert len(entries) == 1
            assert entries[0]["id"] == "doc-id-1"
            assert entries[0]["created_at"] == "2026-06-21T12:00:00+00:00"

    async def test_get_entries_exception_caught(self) -> None:
        """Should log warning and return empty list on get failure."""
        from app.services.firestore_service import get_entries

        mock_client = MagicMock()
        mock_client.collection.side_effect = RuntimeError("Firestore read error")

        with (
            patch("app.services.firestore_service._get_client", return_value=mock_client),
            patch("app.services.firestore_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.use_firestore = True
            mock_settings.return_value.firestore_collection = "test_collection"

            entries = await get_entries("test-001")
            assert entries == []
