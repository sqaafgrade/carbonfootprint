"""Gemini AI service for generating personalized carbon reduction insights.

Key design decisions:
- All imports at the top of the file (ruff PLC0415 compliance).
- Lazy client initialization: the Vertex AI client is only constructed on first
  actual call, so importing this module never fails — even without credentials.
- All user-influenced text is sanitized via ``sanitize_for_prompt`` before
  interpolation into the LLM prompt (defense-in-depth).
- On any exception, ``GeminiUnavailableError`` is raised so routes can fall back
  to deterministic rule-based insights.
"""

from __future__ import annotations

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import vertexai
from vertexai.generative_models import GenerativeModel

from app.core.config import get_settings
from app.core.safety import sanitize_for_prompt

logger = logging.getLogger(__name__)

# Thread executor for running synchronous Vertex AI SDK calls without blocking
# the asyncio event loop.
_executor = ThreadPoolExecutor(max_workers=2)

# Module-level cache for the lazy-initialized model instance.
_model_instance: GenerativeModel | None = None


class GeminiUnavailableError(Exception):
    """Raised when the Gemini service cannot produce a response.

    Routes should catch this and fall back to rule-based insights.
    """


def _get_model() -> GenerativeModel:
    """Lazy-initialize and cache the Vertex AI GenerativeModel.

    The model is only constructed on first call, so this module can be
    safely imported even when no Google Cloud credentials are configured.
    """
    global _model_instance  # noqa: PLW0603
    if _model_instance is None:
        settings = get_settings()
        vertexai.init(project=settings.project_id, location=settings.region)
        _model_instance = GenerativeModel(settings.gemini_model)
        logger.info("Vertex AI GenerativeModel initialized: %s", settings.gemini_model)
    return _model_instance


def _build_prompt(breakdown: dict[str, float], total_kg: float, device_id: str) -> str:
    """Build a structured prompt for Gemini with sanitized inputs."""
    safe_device_id = sanitize_for_prompt(device_id, max_length=64)
    safe_categories = {sanitize_for_prompt(k, max_length=50): v for k, v in breakdown.items()}
    return f"""You are a carbon footprint reduction advisor. Analyze this annual carbon footprint
and provide exactly 3 actionable, specific reduction tips.

User's annual carbon footprint ({safe_device_id}):
- Total: {total_kg:.1f} kg CO₂e/year
- Breakdown: {json.dumps(safe_categories)}

Respond ONLY with a JSON array of exactly 3 objects, each with keys:
- "category": one of "transport", "home", "diet", "consumption", or "general"
- "tip": a specific, actionable tip (50-200 characters)
- "severity": "high", "medium", or "low" based on impact potential

Example format:
[
  {{"category": "transport", "tip": "Switch to cycling for trips under 5km", "severity": "high"}},
  {{"category": "diet", "tip": "Try meatless Mondays", "severity": "medium"}},
  {{"category": "home", "tip": "Switch to LED bulbs", "severity": "low"}}
]

Respond with ONLY the JSON array, no markdown, no explanation."""


def _parse_gemini_response(text: str) -> list[dict[str, str]]:
    """Parse Gemini's text response into structured insights.

    Raises ``GeminiUnavailableError`` if parsing fails.
    """
    cleaned = text.strip()
    # Remove markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:])
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    try:
        parsed: Any = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise GeminiUnavailableError(f"Malformed JSON from Gemini: {exc}") from exc

    if not isinstance(parsed, list) or len(parsed) < 1:
        raise GeminiUnavailableError("Gemini returned empty or non-list response")

    validated: list[dict[str, str]] = []
    for item in parsed[:3]:
        if isinstance(item, dict) and "category" in item and "tip" in item:
            validated.append(
                {
                    "category": str(item.get("category", "general")),
                    "tip": str(item.get("tip", "")),
                    "severity": str(item.get("severity", "medium")),
                }
            )

    if not validated:
        raise GeminiUnavailableError("Gemini response had no valid insight objects")

    return validated


async def get_gemini_insights(
    breakdown: dict[str, float],
    total_kg: float,
    device_id: str,
) -> list[dict[str, str]]:
    """Request personalized insights from Gemini 1.5 Flash.

    Wraps the synchronous Vertex AI SDK call in a thread executor and
    enforces a timeout to prevent event-loop blocking.

    Raises
    ------
    GeminiUnavailableError
        On network error, malformed response, or timeout.
    """
    settings = get_settings()
    prompt = _build_prompt(breakdown, total_kg, device_id)

    try:
        model = _get_model()
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(_executor, model.generate_content, prompt),
            timeout=settings.gemini_timeout_seconds,
        )
        return _parse_gemini_response(response.text)
    except GeminiUnavailableError:
        raise
    except TimeoutError as exc:
        logger.warning("Gemini request timed out after %.1fs", settings.gemini_timeout_seconds)
        raise GeminiUnavailableError("Gemini request timed out") from exc
    except Exception as exc:
        logger.warning("Gemini service error: %s", exc)
        raise GeminiUnavailableError(f"Gemini service error: {exc}") from exc
