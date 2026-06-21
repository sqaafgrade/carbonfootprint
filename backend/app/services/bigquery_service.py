"""BigQuery analytics service for logging calculation events.

Lazy client initialization: the BigQuery client is only created on first use.
This service NEVER raises — all exceptions are caught and logged.
This is critical for fire-and-forget usage from API routes.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from google.cloud import bigquery

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Module-level lazy singleton
_client: bigquery.Client | None = None


def _get_client() -> bigquery.Client:
    """Lazy-initialize the BigQuery client."""
    global _client  # noqa: PLW0603
    if _client is None:
        settings = get_settings()
        _client = bigquery.Client(project=settings.project_id)
        logger.info("BigQuery client initialized for project: %s", settings.project_id)
    return _client


async def log_calculation_event(
    device_id: str,
    total_kg: float,
    breakdown: dict[str, float],
    source: str,
) -> None:
    """Log a calculation event to BigQuery for analytics.

    This function NEVER raises — it logs a warning on any failure.
    Designed for fire-and-forget usage via ``asyncio.create_task()``.
    """
    settings = get_settings()
    if not settings.use_bigquery:
        logger.debug("BigQuery disabled, skipping event log")
        return

    try:
        client = _get_client()
        table_id = f"{settings.project_id}.{settings.bigquery_dataset}.{settings.bigquery_table}"
        rows: list[dict[str, Any]] = [
            {
                "device_id": device_id,
                "total_kg": total_kg,
                "transport_kg": breakdown.get("transport", 0.0),
                "home_kg": breakdown.get("home", 0.0),
                "diet_kg": breakdown.get("diet", 0.0),
                "consumption_kg": breakdown.get("consumption", 0.0),
                "insights_source": source,
                "event_timestamp": datetime.now(tz=UTC).isoformat(),
            }
        ]
        errors = client.insert_rows_json(table_id, rows)
        if errors:
            logger.warning("BigQuery insert errors: %s", errors)
        else:
            logger.info("Logged calculation event to BigQuery for device %s", device_id)
    except Exception:
        logger.warning("Failed to log event to BigQuery", exc_info=True)
