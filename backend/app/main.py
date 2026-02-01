"""
MasterLanguage API. Config-driven dev/prod. HA: health checks, graceful shutdown.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api import auth, videos, users  # register route handlers on routers
from app.core.router import auth_router, user_router, video_router
from app.core.dal.redis import get_redis, close_redis
from app.middleware.logging import LoggingMiddleware
from app.middleware.auth import AuthMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup: ensure Redis is connectable (lazy on first use)
    try:
        r = await get_redis()
        await r.ping()
    except Exception:
        pass  # Log in production; allow app to start for /health to report failure
    yield
    # Shutdown: close Redis
    await close_redis()


app = FastAPI(
    title=_settings.APP_NAME,
    version="2.0.0",
    docs_url="/docs" if _settings.is_development else None,
    redoc_url="/redoc" if _settings.is_development else None,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)  # per-path rate limit; runs after Auth so request.state.user_id is set for uid limits
app.add_middleware(AuthMiddleware)  # JWT validation for protected paths; sets request.state.user_id (runs first = outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Health: HA & fault tolerance ----
@app.get("/health/live")
async def liveness() -> dict:
    """K8s/load balancer liveness: process is up."""
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness() -> dict:
    """Readiness: DB and Redis reachable. Fail here to stop receiving traffic."""
    out: dict = {"status": "ok", "database": "ok", "redis": "ok"}
    try:
        from sqlalchemy import text
        from app.core.dal import engine

        async with engine.connect() as c:
            await c.execute(text("SELECT 1"))
    except Exception as e:
        out["status"] = "degraded"
        out["database"] = str(e)
    try:
        r = await get_redis()
        await r.ping()
    except Exception as e:
        out["status"] = "degraded"
        out["redis"] = str(e)
    return out


# ---- 429 handler: user-friendly message ----
@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
    body = getattr(exc, "detail", {})
    if isinstance(body, dict) and "message" in body:
        return JSONResponse(status_code=429, content=body)
    return JSONResponse(
        status_code=429,
        content={
            "code": "RATE_LIMIT",
            "message": "Too many requests. Please try again later.",
        },
    )


# ---- Routes (APIRouter in app.core.router; handlers in app.api) ----
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(video_router, prefix="/api")


@app.get("/")
async def root() -> dict:
    return {"app": _settings.APP_NAME, "env": _settings.APP_ENV}
