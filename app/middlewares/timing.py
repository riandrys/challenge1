import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.logs import get_logger


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = get_logger()
        start = time.time()
        response = await call_next(request)
        process_time = time.time() - start
        logger.info(
            f"[TIMING] {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.3f}s"
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response
