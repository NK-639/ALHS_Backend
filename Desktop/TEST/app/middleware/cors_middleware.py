"""
CORS 미들웨어 설정

Cross-Origin Resource Sharing (CORS) 정책을 관리합니다.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List


class CORSConfig:
    """CORS 설정 클래스"""

    # 개발 환경 설정
    DEVELOPMENT_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # 프로덕션 환경 설정 (실제 도메인으로 변경 필요)
    PRODUCTION_ORIGINS = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ]

    # 허용할 HTTP 메서드
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

    # 허용할 HTTP 헤더
    ALLOWED_HEADERS = ["*"]

    # 자격 증명 허용 여부
    ALLOW_CREDENTIALS = True


def setup_cors_middleware(
    app: FastAPI,
    allow_origins: List[str] = None,
    allow_development: bool = True
) -> None:
    """
    CORS 미들웨어를 FastAPI 애플리케이션에 추가

    Args:
        app: FastAPI 애플리케이션 인스턴스
        allow_origins: 허용할 origin 리스트 (None이면 기본값 사용)
        allow_development: 개발 환경 origin 허용 여부
    """
    # origin 설정
    if allow_origins is None:
        if allow_development:
            # 개발 환경: 모든 origin 허용 (보안 주의)
            origins = ["*"]
        else:
            # 프로덕션 환경: 특정 origin만 허용
            origins = CORSConfig.PRODUCTION_ORIGINS
    else:
        origins = allow_origins

    # CORS 미들웨어 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=CORSConfig.ALLOW_CREDENTIALS,
        allow_methods=CORSConfig.ALLOWED_METHODS,
        allow_headers=CORSConfig.ALLOWED_HEADERS,
    )


def get_cors_origins(environment: str = "development") -> List[str]:
    """
    환경에 따른 CORS origin 반환

    Args:
        environment: 환경 설정 ("development" 또는 "production")

    Returns:
        List[str]: 허용할 origin 리스트
    """
    if environment == "production":
        return CORSConfig.PRODUCTION_ORIGINS
    else:
        return CORSConfig.DEVELOPMENT_ORIGINS
