"""
커스텀 예외 클래스 정의

애플리케이션에서 발생할 수 있는 다양한 예외 상황을 정의합니다.
"""
from typing import Optional, Any


class BaseAPIException(Exception):
    """
    모든 커스텀 예외의 기본 클래스

    Attributes:
        message: 에러 메시지
        error_code: 에러 코드
        status_code: HTTP 상태 코드
        detail: 상세 설명
        field: 에러가 발생한 필드명
    """

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        detail: Optional[str] = None,
        field: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.detail = detail or message
        self.field = field
        super().__init__(self.message)


class ValidationException(BaseAPIException):
    """
    데이터 유효성 검증 실패

    사용자 입력값이 유효하지 않을 때 발생합니다.

    Examples:
        >>> raise ValidationException(
        ...     message="RPM 값이 유효하지 않습니다",
        ...     error_code="E001",
        ...     detail="RPM은 1-300 사이여야 합니다",
        ...     field="rpm"
        ... )
    """

    def __init__(
        self,
        message: str,
        error_code: str = "VALIDATION_ERROR",
        detail: Optional[str] = None,
        field: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=400,
            detail=detail,
            field=field
        )


class NotFoundException(BaseAPIException):
    """
    리소스를 찾을 수 없음

    요청한 리소스가 존재하지 않을 때 발생합니다.

    Examples:
        >>> raise NotFoundException(
        ...     message="프린터를 찾을 수 없습니다",
        ...     error_code="E404",
        ...     detail="요청한 프린터 ID가 존재하지 않습니다"
        ... )
    """

    def __init__(
        self,
        message: str,
        error_code: str = "NOT_FOUND",
        detail: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=404,
            detail=detail
        )


class KlipperException(BaseAPIException):
    """
    Klipper/Moonraker 통신 오류

    Klipper 또는 Moonraker와의 통신 중 문제가 발생했을 때 사용합니다.

    Examples:
        >>> raise KlipperException(
        ...     message="Klipper 서버 연결 실패",
        ...     error_code="E500",
        ...     detail="Moonraker 서버에 연결할 수 없습니다"
        ... )
    """

    def __init__(
        self,
        message: str,
        error_code: str = "KLIPPER_ERROR",
        detail: Optional[str] = None,
        status_code: int = 503
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            detail=detail
        )


class ServiceException(BaseAPIException):
    """
    서비스 레이어 처리 오류

    비즈니스 로직 처리 중 발생하는 예외입니다.

    Examples:
        >>> raise ServiceException(
        ...     message="G-code 생성 실패",
        ...     error_code="E001",
        ...     detail="유효하지 않은 파라미터입니다"
        ... )
    """

    def __init__(
        self,
        message: str,
        error_code: str = "SERVICE_ERROR",
        detail: Optional[str] = None,
        status_code: int = 500
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            detail=detail
        )


class DuplicateResourceException(BaseAPIException):
    """
    리소스 중복 오류

    이미 존재하는 리소스를 생성하려고 할 때 발생합니다.

    Examples:
        >>> raise DuplicateResourceException(
        ...     message="이미 존재하는 이메일입니다",
        ...     error_code="E409",
        ...     detail="해당 이메일로 이미 가입된 사용자가 있습니다",
        ...     field="email"
        ... )
    """

    def __init__(
        self,
        message: str,
        error_code: str = "DUPLICATE_RESOURCE",
        detail: Optional[str] = None,
        field: Optional[str] = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=409,
            detail=detail,
            field=field
        )


class ExternalAPIException(BaseAPIException):
    """
    외부 API 호출 오류

    외부 API 호출 중 문제가 발생했을 때 사용합니다.

    Examples:
        >>> raise ExternalAPIException(
        ...     message="외부 서버 응답 실패",
        ...     error_code="E502",
        ...     detail="타임아웃이 발생했습니다"
        ... )
    """

    def __init__(
        self,
        message: str,
        error_code: str = "EXTERNAL_API_ERROR",
        detail: Optional[str] = None,
        status_code: int = 502
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=status_code,
            detail=detail
        )
