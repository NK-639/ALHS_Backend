"""로깅 미들웨어"""
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.logging_config import get_logger
from app.utils.trace import generate_trace_id, set_trace_id, get_trace_id, clear_trace_id

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP 요청/응답 로깅 및 처리 시간 측정"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        trace_id = generate_trace_id()
        set_trace_id(trace_id)
        start_time = time.time()

        logger.info(
            f"📥 Request: {request.method} {request.url.path} "
            f"- Client: {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            logger.info(
                f"📤 Response: {request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Time: {process_time:.3f}s"
            )

            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"❌ Error: {request.method} {request.url.path} "
                f"- Error: {str(e)} "
                f"- Time: {process_time:.3f}s",
                exc_info=True
            )
            raise
        finally:
            clear_trace_id()
