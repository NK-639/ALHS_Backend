"""
공통 응답 스키마

모든 API의 응답을 일관된 형식으로 반환하기 위한 스키마입니다.
"""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field


# 제네릭 타입 변수 정의
T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """
    공통 API 응답 형식

    모든 API는 이 형식으로 응답을 반환합니다.

    Attributes:
        success: 요청 성공 여부 (True/False)
        message: 응답 메시지
        data: 응답 데이터 (제네릭 타입)
        error: 에러 정보 (실패 시에만 포함)

    Examples:
        >>> # 성공 응답
        >>> ApiResponse(success=True, message="성공", data={"id": 1})

        >>> # 실패 응답
        >>> ApiResponse(success=False, message="실패", error={"code": "E001"})
    """
    success: bool = Field(
        ...,
        description="요청 성공 여부"
    )
    message: str = Field(
        ...,
        description="응답 메시지",
        min_length=1
    )
    data: Optional[T] = Field(
        default=None,
        description="응답 데이터 (성공 시)"
    )
    error: Optional[dict[str, Any]] = Field(
        default=None,
        description="에러 상세 정보 (실패 시)"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "success": True,
                    "message": "프린터 실행 준비 완료",
                    "data": {
                        "printer_id": "main_printer",
                        "status": "ready"
                    }
                }
            ]
        }


class ErrorDetail(BaseModel):
    """
    에러 상세 정보

    Attributes:
        code: 에러 코드 (예: E001, E404)
        detail: 상세 설명
        field: 에러가 발생한 필드명 (있는 경우)
    """
    code: str = Field(
        ...,
        description="에러 코드"
    )
    detail: str = Field(
        ...,
        description="에러 상세 설명"
    )
    field: Optional[str] = Field(
        default=None,
        description="에러 발생 필드"
    )


# Type aliases for convenience
SuccessResponse = ApiResponse
ErrorResponse = ApiResponse


def create_success_response(
    message: str,
    data: Any = None
) -> dict:
    """
    성공 응답 생성 헬퍼 함수

    Args:
        message: 성공 메시지
        data: 응답 데이터

    Returns:
        dict: ApiResponse 형식의 딕셔너리

    Examples:
        >>> create_success_response("조회 완료", {"id": 1, "name": "test"})
        {'success': True, 'message': '조회 완료', 'data': {...}}
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }


def create_error_response(
    message: str,
    error_code: str = "UNKNOWN_ERROR",
    error_detail: Optional[str] = None,
    field: Optional[str] = None
) -> dict:
    """
    에러 응답 생성 헬퍼 함수

    Args:
        message: 에러 메시지
        error_code: 에러 코드
        error_detail: 상세 설명
        field: 에러 발생 필드

    Returns:
        dict: ApiResponse 형식의 딕셔너리

    Examples:
        >>> create_error_response(
        ...     "유효하지 않은 입력",
        ...     error_code="E001",
        ...     error_detail="RPM은 1-300 사이여야 합니다",
        ...     field="rpm"
        ... )
    """
    error_info = {
        "code": error_code,
        "detail": error_detail or message
    }

    if field:
        error_info["field"] = field

    return {
        "success": False,
        "message": message,
        "error": error_info
    }
