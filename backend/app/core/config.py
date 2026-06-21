"""Application configuration via environment variables with Pydantic settings.

All settings have safe defaults that allow the app to boot without any
external services configured (graceful degradation).
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Typed, validated application settings loaded from environment."""

    # ── Project identification ─────────────────────────────────────────
    project_id: str = "carbon-platform-dev"  # Example: carbonfootprint-sakshi
    region: str = "us-central1"
    environment: Literal["development", "staging", "production"] = "development"

    # ── Feature flags (graceful degradation) ───────────────────────────
    use_gemini: bool = False
    use_firestore: bool = False
    use_bigquery: bool = False
    use_pubsub: bool = False

    # ── Gemini / Vertex AI ─────────────────────────────────────────────
    gemini_model: str = "gemini-1.5-flash"
    gemini_timeout_seconds: float = 8.0

    # ── Firestore ──────────────────────────────────────────────────────
    firestore_collection: str = "carbon_entries"

    # ── BigQuery ───────────────────────────────────────────────────────
    bigquery_dataset: str = "carbon_analytics"
    bigquery_table: str = "calculation_events"

    # ── Pub/Sub ────────────────────────────────────────────────────────
    pubsub_topic: str = "carbon-calculations"

    # ── Rate limiting ──────────────────────────────────────────────────
    rate_limit_per_minute: int = 30

    # ── CORS ───────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse the comma-separated CORS origins string into a list."""
        return [origin.strip() for origin in re.split(r"[,;]", self.cors_origins) if origin.strip()]

    model_config = {"env_prefix": "", "case_sensitive": False, "env_file": ".env"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the cached singleton settings instance."""
    return Settings()
