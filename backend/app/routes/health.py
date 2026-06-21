"""Health check endpoint.

Provides a simple liveness probe for Cloud Run and Docker health checks.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(
    "/api/health",
    summary="Health check",
    description="Returns service status for load balancer and container orchestrator probes.",
    response_model=dict[str, str],
)
async def health_check() -> dict[str, str]:
    """Return a simple health status response."""
    return {"status": "healthy", "service": "carbon-platform"}
