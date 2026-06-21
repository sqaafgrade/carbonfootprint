"""Carbon footprint calculation endpoint.

Accepts user inputs, runs the pure calculator, optionally enriches with
Gemini AI insights (with rule-based fallback), and fires off async tasks
for BigQuery logging and Pub/Sub publishing.
"""

import asyncio
import logging
from typing import Any, cast

from fastapi import APIRouter, Request

from app.carbon.calculator import calculate_footprint, get_rule_based_insights
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.models.carbon import CarbonInput, CarbonResult
from app.services.bigquery_service import log_calculation_event
from app.services.gemini_service import GeminiUnavailableError, get_gemini_insights
from app.services.pubsub_service import publish_calculation_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["calculate"])

_BACKGROUND_TASKS: set[asyncio.Task[None]] = set()


@router.post(
    "/calculate",
    response_model=CarbonResult,
    summary="Calculate carbon footprint",
    description="Accepts lifestyle inputs and returns a detailed carbon footprint "
    "breakdown with actionable reduction insights.",
)
@limiter.limit("30/minute")
async def calculate(request: Request, data: CarbonInput) -> CarbonResult:
    """Calculate carbon footprint and return insights.

    Flow:
    1. Run pure calculation (zero I/O).
    2. If Gemini is enabled, attempt AI insights; on any failure, fall back to rules.
    3. Fire-and-forget: log to BigQuery and publish to Pub/Sub.
    4. Return result immediately.
    """
    settings = get_settings()
    inputs = data.model_dump()
    result = calculate_footprint(inputs)

    # Attempt Gemini insights with automatic fallback
    source = "rules"
    if settings.use_gemini:
        try:
            insights = await get_gemini_insights(
                breakdown=cast(dict[str, float], result["breakdown"]),
                total_kg=cast(float, result["total_kg"]),
                device_id=data.device_id,
            )
            source = "gemini"
        except GeminiUnavailableError as exc:
            logger.info("Gemini unavailable, using rule-based fallback: %s", exc)
            insights = get_rule_based_insights(
                cast(list[dict[str, Any]], result["ranked_categories"]),
                cast(dict[str, float], result["breakdown"]),
            )
    else:
        insights = get_rule_based_insights(
            cast(list[dict[str, Any]], result["ranked_categories"]),
            cast(dict[str, float], result["breakdown"]),
        )

    # Fire-and-forget async tasks for analytics (never block the response)
    breakdown = cast(dict[str, float], result["breakdown"])
    task1 = asyncio.create_task(
        log_calculation_event(
            device_id=data.device_id,
            total_kg=cast(float, result["total_kg"]),
            breakdown=breakdown,
            source=source,
        )
    )
    _BACKGROUND_TASKS.add(task1)
    task1.add_done_callback(_BACKGROUND_TASKS.discard)

    task2 = asyncio.create_task(
        publish_calculation_event(
            device_id=data.device_id,
            total_kg=cast(float, result["total_kg"]),
            breakdown=breakdown,
        )
    )
    _BACKGROUND_TASKS.add(task2)
    task2.add_done_callback(_BACKGROUND_TASKS.discard)

    return CarbonResult(
        total_kg=cast(float, result["total_kg"]),
        breakdown=cast(Any, result["breakdown"]),
        vs_global_average_pct=cast(float, result["vs_global_average_pct"]),
        vs_paris_target_pct=cast(float, result["vs_paris_target_pct"]),
        ranked_categories=cast(Any, result["ranked_categories"]),
        insights=insights,
        source=cast(Any, source),
    )
