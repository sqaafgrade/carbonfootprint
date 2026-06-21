"""History entries endpoint — CRUD for carbon footprint tracking entries.

Allows users to retrieve their historical footprint calculations.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query, Request

from app.core.rate_limit import limiter
from app.services.firestore_service import get_entries

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["entries"])


@router.get(
    "/entries",
    summary="Get calculation history",
    description="Retrieves the most recent carbon footprint calculations for a device. "
    "Returns an empty list if Firestore is disabled or unavailable.",
    response_model=list[dict[str, Any]],
)
@limiter.limit("30/minute")
async def list_entries(
    request: Request,
    device_id: str = Query(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z0-9\-]+$",
        description="Anonymous device identifier",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of entries to return (1–100)",
    ),
) -> list[dict[str, Any]]:
    """Retrieve historical carbon footprint entries for a device."""
    entries = await get_entries(device_id=device_id, limit=limit)
    return entries
