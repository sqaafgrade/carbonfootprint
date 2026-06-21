"""FastAPI application factory.

Uses ``create_app()`` factory pattern (not a bare module-level ``app``) so
tests can construct fresh app instances with different settings per test.
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import FileResponse

from app.core.config import Settings, get_settings
from app.core.rate_limit import limiter
from app.core.security import configure_cors, security_headers_middleware
from app.routes.calculate import router as calculate_router
from app.routes.entries import router as entries_router
from app.routes.health import router as health_router
from app.routes.insights import router as insights_router

logger = logging.getLogger(__name__)

# Path to the built frontend SPA static files
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure a FastAPI application instance.

    Parameters
    ----------
    settings:
        Optional settings override (used in tests). If ``None``, uses
        the default singleton from ``get_settings()``.
    """
    if settings is None:
        settings = get_settings()

    # Configure structured logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    app = FastAPI(
        title="Carbon Footprint Awareness Platform",
        description="Personal carbon footprint education and reduction platform. "
        "Understand → Track → Reduce.",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Security middleware
    app.middleware("http")(security_headers_middleware)
    configure_cors(app, settings.cors_origin_list)

    # API routes
    app.include_router(health_router)
    app.include_router(calculate_router)
    app.include_router(insights_router)
    app.include_router(entries_router)

    # Mount static SPA conditionally — if the static/ directory doesn't exist
    # (e.g., in CI before frontend build), the API still boots and serves
    # JSON endpoints; only the catch-all SPA route is skipped.
    if STATIC_DIR.exists() and STATIC_DIR.is_dir():
        app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(request: Request, full_path: str) -> FileResponse:
            """Serve the SPA index.html for all non-API routes."""
            file_path = STATIC_DIR / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(STATIC_DIR / "index.html"))

        logger.info("Serving SPA from %s", STATIC_DIR)
    else:
        logger.info("Static directory %s not found — running in API-only mode", STATIC_DIR)

    logger.info(
        "App created: environment=%s, gemini=%s, firestore=%s, bigquery=%s, pubsub=%s",
        settings.environment,
        settings.use_gemini,
        settings.use_firestore,
        settings.use_bigquery,
        settings.use_pubsub,
    )

    return app


# The module-level app instance used by uvicorn in production:
#   uvicorn app.main:app --host 0.0.0.0 --port 8080
app = create_app()
