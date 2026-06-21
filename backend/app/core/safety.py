"""Input/output safety guards — applied before any text reaches the Gemini prompt.

Demonstrates defense-in-depth: even though current input fields are mostly
constrained enums and numbers, all string values are sanitized before they
are interpolated into LLM prompts or persisted.
"""

from __future__ import annotations

import re

EMAIL_PATTERN: re.Pattern[str] = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_PATTERN: re.Pattern[str] = re.compile(r"\b\d{10}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")
SSN_PATTERN: re.Pattern[str] = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_pii(text: str) -> str:
    """Redact email, phone, and SSN patterns from any free text.

    Applied before text is logged or sent to an LLM.

    >>> redact_pii("Contact john@example.com or 555-123-4567")
    'Contact [EMAIL_REDACTED] or [PHONE_REDACTED]'
    >>> redact_pii("SSN: 123-45-6789")
    'SSN: [SSN_REDACTED]'
    """
    text = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)
    text = PHONE_PATTERN.sub("[PHONE_REDACTED]", text)
    return SSN_PATTERN.sub("[SSN_REDACTED]", text)


def sanitize_for_prompt(value: str, max_length: int = 200) -> str:
    r"""Defensive sanitization before any value is interpolated into an LLM prompt.

    1. Strips control characters (0x00–0x1f, 0x7f) to prevent prompt injection
       via invisible characters.
    2. Redacts PII patterns.
    3. Truncates to ``max_length`` to prevent prompt injection via length abuse.

    >>> sanitize_for_prompt("normal input")
    'normal input'
    >>> sanitize_for_prompt("has\x00null\x1fchars")
    'hasnullchars'
    >>> len(sanitize_for_prompt("a" * 500, max_length=200))
    200
    """
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", value)
    return redact_pii(cleaned)[:max_length]
