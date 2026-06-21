"""Firestore service for persisting carbon footprint entries.

Lazy client initialization: the Firestore client is only created on first use,
so the app can boot cleanly with ``USE_FIRESTORE=false``.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from google.cloud import firestore

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Module-level lazy singleton
_client: firestore.AsyncClient | None = None


def _get_client() -> firestore.AsyncClient:
    """Lazy-initialize the Firestore async client."""
    global _client  # noqa: PLW0603
    if _client is None:
        settings = get_settings()
        _client = firestore.AsyncClient(project=settings.project_id)
        logger.info("Firestore AsyncClient initialized for project: %s", settings.project_id)
    return _client


async def save_entry(device_id: str, result: dict[str, Any]) -> str | None:
    """Persist a carbon calculation entry to Firestore.

    Returns the document ID on success, or ``None`` on failure.
    Never raises — logs a warning on any error (fire-and-forget safe).
    """
    settings = get_settings()
    if not settings.use_firestore:
        logger.debug("Firestore disabled, skipping save")
        return None

    try:
        client = _get_client()
        collection = client.collection(settings.firestore_collection)
        doc_data = {
            "device_id": device_id,
            "total_kg": result.get("total_kg", 0),
            "breakdown": result.get("breakdown", {}),
            "insights_source": result.get("source", "rules"),
            "created_at": datetime.now(tz=UTC),
        }
        doc_ref = await collection.add(doc_data)
        doc_id = doc_ref[1].id
        logger.info("Saved entry %s for device %s", doc_id, device_id)
        return doc_id
    except Exception:
        logger.warning("Failed to save entry to Firestore", exc_info=True)
        return None


async def get_entries(device_id: str, limit: int = 50) -> list[dict[str, Any]]:
    """Retrieve recent carbon entries for a device.

    Never raises — returns an empty list on failure.
    """
    settings = get_settings()
    if not settings.use_firestore:
        logger.debug("Firestore disabled, returning empty history")
        return []

    try:
        client = _get_client()
        collection = client.collection(settings.firestore_collection)
        query = (
            collection.where("device_id", "==", device_id)
            .order_by("created_at", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        docs = []
        async for doc in query.stream():
            data = doc.to_dict()
            if data:
                data["id"] = doc.id
                # Convert Firestore timestamps to ISO strings for JSON serialization
                if "created_at" in data and hasattr(data["created_at"], "isoformat"):
                    data["created_at"] = data["created_at"].isoformat()
                docs.append(data)
        return docs
    except Exception:
        logger.warning("Failed to fetch entries from Firestore", exc_info=True)
        return []
