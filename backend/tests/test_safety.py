"""Tests for the safety module — PII redaction and prompt sanitization.

Verifies that:
- redact_pii correctly redacts emails, phone numbers, and SSNs.
- sanitize_for_prompt strips control characters, redacts PII, and enforces
  length limits.
"""

from __future__ import annotations

from app.core.safety import redact_pii, sanitize_for_prompt


class TestRedactPii:
    """Tests for the PII redaction function."""

    def test_redacts_email(self) -> None:
        """Email addresses should be replaced with [EMAIL_REDACTED]."""
        text = "Contact john.doe@example.com for details"
        result = redact_pii(text)
        assert "[EMAIL_REDACTED]" in result
        assert "john.doe@example.com" not in result

    def test_redacts_multiple_emails(self) -> None:
        """Multiple emails should all be redacted."""
        text = "Send to alice@test.org and bob@corp.com"
        result = redact_pii(text)
        assert result.count("[EMAIL_REDACTED]") == 2

    def test_redacts_phone_with_dashes(self) -> None:
        """Phone numbers with dashes should be redacted."""
        text = "Call me at 555-123-4567"
        result = redact_pii(text)
        assert "[PHONE_REDACTED]" in result
        assert "555-123-4567" not in result

    def test_redacts_phone_with_dots(self) -> None:
        """Phone numbers with dots should be redacted."""
        text = "Phone: 555.123.4567"
        result = redact_pii(text)
        assert "[PHONE_REDACTED]" in result

    def test_redacts_phone_with_spaces(self) -> None:
        """Phone numbers with spaces should be redacted."""
        text = "Call 555 123 4567 now"
        result = redact_pii(text)
        assert "[PHONE_REDACTED]" in result

    def test_redacts_10_digit_phone(self) -> None:
        """10-digit continuous phone number should be redacted."""
        text = "Number is 5551234567 here"
        result = redact_pii(text)
        assert "[PHONE_REDACTED]" in result

    def test_redacts_ssn(self) -> None:
        """SSN pattern should be redacted."""
        text = "SSN: 123-45-6789"
        result = redact_pii(text)
        assert "[SSN_REDACTED]" in result
        assert "123-45-6789" not in result

    def test_preserves_non_pii_text(self) -> None:
        """Normal text without PII should be unchanged."""
        text = "I drive a petrol car 30 km daily"
        result = redact_pii(text)
        assert result == text

    def test_mixed_pii(self) -> None:
        """Text with multiple PII types should have all redacted."""
        text = "Contact jane@test.com or 555-000-1234"
        result = redact_pii(text)
        assert "[EMAIL_REDACTED]" in result
        assert "[PHONE_REDACTED]" in result
        assert "jane@test.com" not in result
        assert "555-000-1234" not in result


class TestSanitizeForPrompt:
    """Tests for the prompt sanitization function."""

    def test_normal_text_unchanged(self) -> None:
        """Clean text should pass through unchanged."""
        result = sanitize_for_prompt("car_petrol")
        assert result == "car_petrol"

    def test_strips_null_bytes(self) -> None:
        """Null bytes (\\x00) should be stripped."""
        result = sanitize_for_prompt("before\x00after")
        assert result == "beforeafter"
        assert "\x00" not in result

    def test_strips_control_characters(self) -> None:
        """Control characters (0x00–0x1f, 0x7f) should be stripped."""
        result = sanitize_for_prompt("hello\x01\x02\x1f\x7fworld")
        assert result == "helloworld"

    def test_strips_newlines_and_tabs(self) -> None:
        """Newlines and tabs (control chars) should be stripped."""
        result = sanitize_for_prompt("line1\nline2\ttab")
        assert "\n" not in result
        assert "\t" not in result

    def test_truncates_to_max_length(self) -> None:
        """Output should be truncated to max_length."""
        result = sanitize_for_prompt("a" * 500, max_length=200)
        assert len(result) == 200

    def test_custom_max_length(self) -> None:
        """Custom max_length should be respected."""
        result = sanitize_for_prompt("a" * 100, max_length=50)
        assert len(result) == 50

    def test_redacts_pii_before_truncation(self) -> None:
        """PII should be redacted (then truncated if needed)."""
        result = sanitize_for_prompt("user@example.com is here")
        assert "user@example.com" not in result
        assert "[EMAIL_REDACTED]" in result

    def test_combines_all_sanitization(self) -> None:
        """Control char removal + PII redaction + truncation should all apply."""
        evil_input = "\x00user@evil.com\x01" + "a" * 300
        result = sanitize_for_prompt(evil_input, max_length=100)
        assert "\x00" not in result
        assert "user@evil.com" not in result
        assert len(result) <= 100

    def test_empty_string(self) -> None:
        """Empty string should return empty string."""
        assert sanitize_for_prompt("") == ""
