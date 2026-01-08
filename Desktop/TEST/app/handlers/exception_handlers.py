"""예외 처리 핸들러"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from app.exceptions.custom_exceptions import BaseAPIException
from app.common.schemas.common_schemas import create_error_response
from app.config import get_logger
from app.utils.trace import get_trace_id

logger = get_logger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """예외 핸들러 등록"""

    @app.exception_handler(BaseAPIException)
    async def custom_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
        """커스텀 예외 처리"""
        logger.error(
            f"❌ Custom Exception: {exc.error_code} - {exc.message}",
            extra={
                "error_code": exc.error_code,
                "detail": exc.detail,
                "field": exc.field,
                "path": request.url.path,
                "method": request.method
            }
        )

        response = create_error_response(
            message=exc.message,
            error_code=exc.error_code,
            error_detail=exc.detail,
            field=exc.field
        )

        headers = {}
        trace_id = get_trace_id()
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        return JSONResponse(status_code=exc.status_code, content=response, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Pydantic 유효성 검증 에러 처리"""
        errors = exc.errors()
        first_error = errors[0] if errors else {}

        field_path = " -> ".join(str(loc) for loc in first_error.get("loc", []))
        error_msg = first_error.get("msg", "유효성 검증 실패")

        logger.warning(
            f"⚠️ Validation Error: {field_path} - {error_msg}",
            extra={"errors": errors, "path": request.url.path, "method": request.method}
        )

        response = create_error_response(
            message="입력 데이터가 유효하지 않습니다",
            error_code="VALIDATION_ERROR",
            error_detail=error_msg,
            field=field_path
        )

        headers = {}
        trace_id = get_trace_id()
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response, headers=headers)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Pydantic 모델 검증 에러 처리"""
        errors = exc.errors()
        first_error = errors[0] if errors else {}

        field_path = " -> ".join(str(loc) for loc in first_error.get("loc", []))
        error_msg = first_error.get("msg", "유효성 검증 실패")

        logger.warning(
            f"⚠️ Pydantic Validation Error: {field_path} - {error_msg}",
            extra={"errors": errors, "path": request.url.path}
        )

        response = create_error_response(
            message="데이터 검증 실패",
            error_code="VALIDATION_ERROR",
            error_detail=error_msg,
            field=field_path
        )

        headers = {}
        trace_id = get_trace_id()
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=response, headers=headers)

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """일반 예외 처리 (처리되지 않은 모든 예외)"""
        logger.error(
            f"❌ Unhandled Exception: {type(exc).__name__} - {str(exc)}",
            exc_info=True,
            extra={"path": request.url.path, "method": request.method}
        )

        response = create_error_response(
            message="서버 내부 오류가 발생했습니다",
            error_code="INTERNAL_SERVER_ERROR",
            error_detail=str(exc)
        )

        headers = {}
        trace_id = get_trace_id()
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response, headers=headers)
