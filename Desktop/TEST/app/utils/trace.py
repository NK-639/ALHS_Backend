"""Trace ID 관리 모듈"""
import uuid
from contextvars import ContextVar
from typing import Optional

_trace_id_ctx: ContextVar[Optional[str]] = ContextVar('trace_id', default=None)


def generate_trace_id() -> str:
    """UUID 기반 Trace ID 생성"""
    return str(uuid.uuid4())


def set_trace_id(trace_id: str) -> None:
    """컨텍스트에 Trace ID 설정"""
    _trace_id_ctx.set(trace_id)


def get_trace_id() -> Optional[str]:
    """컨텍스트의 Trace ID 조회"""
    return _trace_id_ctx.get()


def clear_trace_id() -> None:
    """Trace ID 초기화"""
    _trace_id_ctx.set(None)
