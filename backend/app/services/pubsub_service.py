"""Pub/Sub messaging service for publishing calculation events.

Lazy client initialization: the Pub/Sub publisher is only created on first use.
This service NEVER raises — all exceptions are caught and logged.
This is critical for fire-and-forget usage from API routes.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from google.cloud import pubsub_v1

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Module-level lazy singleton
_publisher: pubsub_v1.PublisherClient | None = None


def _get_publisher() -> pubsub_v1.PublisherClient:
    """Lazy-initialize the Pub/Sub publisher client."""
    global _publisher  # noqa: PLW0603
    if _publisher is None:
        _publisher = pubsub_v1.PublisherClient()
        logger.info("Pub/Sub PublisherClient initialized")
    return _publisher


async def publish_calculation_event(
    device_id: str,
    total_kg: float,
    breakdown: dict[str, float],
) -> None:
    """Publish a calculation event to Pub/Sub for downstream consumers.

    This function NEVER raises — it logs a warning on any failure.
    Designed for fire-and-forget usage via ``asyncio.create_task()``.
    """
    settings = get_settings()
    if not settings.use_pubsub:
        logger.debug("Pub/Sub disabled, skipping event publish")
        return

    try:
        publisher = _get_publisher()
        topic_path = publisher.topic_path(settings.project_id, settings.pubsub_topic)
        message_data: dict[str, Any] = {
            "device_id": device_id,
            "total_kg": total_kg,
            "breakdown": breakdown,
        }
        data_bytes = json.dumps(message_data).encode("utf-8")
        future = publisher.publish(topic_path, data=data_bytes)
        message_id = future.result(timeout=5.0)
        logger.info("Published event %s to Pub/Sub for device %s", message_id, device_id)
    except Exception:
        logger.warning("Failed to publish event to Pub/Sub", exc_info=True)
