"""
예외 핸들러 모듈

애플리케이션에서 발생하는 예외를 처리하는 핸들러들을 정의합니다.
"""
from app.handlers.exception_handlers import setup_exception_handlers

__all__ = ["setup_exception_handlers"]
