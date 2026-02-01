"""
Request/response logging middleware. Logs method, path, status, duration.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log each request: method, path, status code, duration (seconds)."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        method = request.method
        path = request.url.path
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.exception("Request failed: %s %s", method, path)
            raise
        duration = time.perf_counter() - start
        logger.info(
            "%s %s %s %.3fs",
            method,
            path,
            status_code,
            duration,
            extra={"method": method, "path": path, "status": status_code, "duration_s": duration},
        )
        return response
