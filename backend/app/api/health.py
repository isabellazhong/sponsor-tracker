"""Liveness/readiness endpoint. Readiness means the database answers a query."""

import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas.health import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> HealthResponse:
    try:
        await session.execute(text("SELECT 1"))
    # Broad on purpose: connection-time failures surface as raw driver errors
    # (e.g. asyncpg.InvalidCatalogNameError) that SQLAlchemy never wraps, and a
    # health check must report them rather than return a 500.
    except Exception as exc:  # noqa: BLE001  # pragma: no cover - needs a down DB
        logger.warning("health check: database unreachable: %s", exc)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status="degraded", database="error")

    return HealthResponse(status="ok", database="ok")
