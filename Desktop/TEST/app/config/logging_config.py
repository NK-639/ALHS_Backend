"""로깅 설정 모듈"""
import logging
import sys
from pathlib import Path
from typing import Optional
from app.utils.trace import get_trace_id


class TraceIdFilter(logging.Filter):
    """로그 레코드에 Trace ID를 추가하는 필터"""

    def filter(self, record: logging.LogRecord) -> bool:
        trace_id = get_trace_id()
        record.trace_id = trace_id if trace_id else "no-trace"
        return True


class LogConfig:
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s - [%(trace_id)s] - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    LOG_DIR = Path("logs")
    LOG_FILE = LOG_DIR / "app.log"
    ERROR_LOG_FILE = LOG_DIR / "error.log"

    @classmethod
    def setup_logging(cls, log_level: Optional[int] = None) -> None:
        """로깅 시스템 초기화"""
        cls.LOG_DIR.mkdir(exist_ok=True)
        level = log_level or cls.LOG_LEVEL

        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        formatter = logging.Formatter(fmt=cls.LOG_FORMAT, datefmt=cls.DATE_FORMAT)
        trace_filter = TraceIdFilter()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(trace_filter)
        root_logger.addHandler(console_handler)

        file_handler = logging.FileHandler(cls.LOG_FILE, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(trace_filter)
        root_logger.addHandler(file_handler)

        error_handler = logging.FileHandler(cls.ERROR_LOG_FILE, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        error_handler.addFilter(trace_filter)
        root_logger.addHandler(error_handler)

        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 반환"""
    return logging.getLogger(name)
