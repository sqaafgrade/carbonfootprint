"""Insights endpoint — returns personalized reduction insights.

Provides AI-powered insights when Gemini is available, with automatic
fallback to deterministic rule-based insights.
"""

import logging

from fastapi import APIRouter, Request

from app.carbon.calculator import calculate_footprint, get_rule_based_insights
from app.core.config import get_settings
from app.core.rate_limit import limiter
from app.models.carbon import CarbonInput
from app.models.insights import Insight, InsightsResponse
from app.services.gemini_service import GeminiUnavailableError, get_gemini_insights

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["insights"])


@router.post(
    "/insights",
    response_model=InsightsResponse,
    summary="Get reduction insights",
    description="Generates personalized carbon reduction insights based on the user's "
    "footprint profile. Uses Gemini AI when available, falls back to rule-based insights.",
)
@limiter.limit("20/minute")
async def get_insights(request: Request, data: CarbonInput) -> InsightsResponse:
    """Generate insights for a given carbon footprint input."""
    settings = get_settings()
    inputs = data.model_dump()
    result = calculate_footprint(inputs)

    source = "rules"
    if settings.use_gemini:
        try:
            insights = await get_gemini_insights(
                breakdown=result["breakdown"],  # type: ignore[arg-type]
                total_kg=float(result["total_kg"]),  # type: ignore[arg-type]
                device_id=data.device_id,
            )
            source = "gemini"
        except GeminiUnavailableError as exc:
            logger.info("Gemini unavailable for insights, using fallback: %s", exc)
            insights = get_rule_based_insights(
                result["ranked_categories"],  # type: ignore[arg-type]
                result["breakdown"],  # type: ignore[arg-type]
            )
    else:
        insights = get_rule_based_insights(
            result["ranked_categories"],  # type: ignore[arg-type]
            result["breakdown"],  # type: ignore[arg-type]
        )

    return InsightsResponse(
        insights=[
            Insight(category=i["category"], tip=i["tip"], severity=i["severity"]) for i in insights
        ],
        source=source,
        device_id=data.device_id,
    )
