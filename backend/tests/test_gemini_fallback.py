"""Tests for Gemini service fallback behavior.

Explicitly tests 3 distinct failure modes:
1. Network error → rule-based fallback
2. Malformed JSON response → rule-based fallback
3. Timeout → rule-based fallback

All tests are fully offline — Vertex AI SDK is mocked.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.services.gemini_service import (
    GeminiUnavailableError,
    _parse_gemini_response,
    get_gemini_insights,
)


class TestParseGeminiResponse:
    """Tests for the response parser."""

    def test_valid_json_array(self) -> None:
        """Should parse a valid JSON array of insights."""
        text = '[{"category": "transport", "tip": "Ride a bike to work", "severity": "high"}]'
        result = _parse_gemini_response(text)
        assert len(result) == 1
        assert result[0]["category"] == "transport"
        assert result[0]["severity"] == "high"

    def test_json_with_markdown_fences(self) -> None:
        """Should handle markdown code-fenced JSON."""
        text = '```json\n[{"category": "diet", "tip": "Try meatless Monday is a good idea", "severity": "medium"}]\n```'
        result = _parse_gemini_response(text)
        assert len(result) == 1
        assert result[0]["category"] == "diet"

    def test_malformed_json_raises(self) -> None:
        """Should raise GeminiUnavailableError for invalid JSON."""
        with pytest.raises(GeminiUnavailableError, match="Malformed JSON"):
            _parse_gemini_response("this is not json at all")

    def test_empty_array_raises(self) -> None:
        """Should raise GeminiUnavailableError for empty array."""
        with pytest.raises(GeminiUnavailableError, match="empty"):
            _parse_gemini_response("[]")

    def test_non_list_raises(self) -> None:
        """Should raise GeminiUnavailableError for non-list JSON."""
        with pytest.raises(GeminiUnavailableError, match="empty"):
            _parse_gemini_response('{"key": "value"}')

    def test_truncates_to_three(self) -> None:
        """Should return at most 3 insights even if more are provided."""
        text = """[
            {"category": "a", "tip": "tip 1 text here", "severity": "high"},
            {"category": "b", "tip": "tip 2 text here", "severity": "medium"},
            {"category": "c", "tip": "tip 3 text here", "severity": "low"},
            {"category": "d", "tip": "tip 4 text here", "severity": "low"}
        ]"""
        result = _parse_gemini_response(text)
        assert len(result) == 3


class TestGeminiFallback:
    """Tests for the 3 distinct failure modes."""

    @pytest.fixture(autouse=True)
    def _reset_model(self) -> None:
        """Reset the cached model instance before each test."""
        import app.services.gemini_service as svc

        svc._model_instance = None

    async def test_network_error_raises_unavailable(self) -> None:
        """Network failure should raise GeminiUnavailableError."""
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = ConnectionError("Network unreachable")

        with (
            patch("app.services.gemini_service._get_model", return_value=mock_model),
            patch("app.services.gemini_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.gemini_timeout_seconds = 5.0
            mock_settings.return_value.project_id = "test"
            mock_settings.return_value.region = "us-central1"
            with pytest.raises(GeminiUnavailableError, match="service error"):
                await get_gemini_insights(
                    breakdown={"transport": 1000.0},
                    total_kg=1000.0,
                    device_id="test-device",
                )

    async def test_malformed_response_raises_unavailable(self) -> None:
        """Malformed Gemini response should raise GeminiUnavailableError."""
        mock_response = MagicMock()
        mock_response.text = "not valid json response"
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response

        with (
            patch("app.services.gemini_service._get_model", return_value=mock_model),
            patch("app.services.gemini_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.gemini_timeout_seconds = 5.0
            mock_settings.return_value.project_id = "test"
            mock_settings.return_value.region = "us-central1"
            with pytest.raises(GeminiUnavailableError, match="Malformed JSON"):
                await get_gemini_insights(
                    breakdown={"transport": 1000.0},
                    total_kg=1000.0,
                    device_id="test-device",
                )

    async def test_timeout_raises_unavailable(self) -> None:
        """Timeout should raise GeminiUnavailableError."""

        def slow_generate(*args, **kwargs):  # type: ignore[no-untyped-def]
            import time

            time.sleep(10)
            return MagicMock(text="[]")

        mock_model = MagicMock()
        mock_model.generate_content.side_effect = slow_generate

        with (
            patch("app.services.gemini_service._get_model", return_value=mock_model),
            patch("app.services.gemini_service.get_settings") as mock_settings,
        ):
            mock_settings.return_value.gemini_timeout_seconds = 0.1
            mock_settings.return_value.project_id = "test"
            mock_settings.return_value.region = "us-central1"
            with pytest.raises(GeminiUnavailableError, match="timed out"):
                await get_gemini_insights(
                    breakdown={"transport": 1000.0},
                    total_kg=1000.0,
                    device_id="test-device",
                )
