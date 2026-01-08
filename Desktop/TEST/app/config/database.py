"""데이터베이스 연결 설정"""
import os
from pathlib import Path
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, QueuePool, StaticPool
from app.config import get_logger

logger = get_logger(__name__)

Base = declarative_base()

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent.parent


class DatabaseConfig:
    # DB 타입 선택: 'sqlite' 또는 'mysql' (기본값: sqlite)
    DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

    # SQLite 설정
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(PROJECT_ROOT / "test.db"))

    # MySQL 설정
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "shaker_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "shakerpassword")
    DB_NAME = os.getenv("DB_NAME", "shaker_db")

    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    @classmethod
    def get_database_url(cls) -> str:
        """
        데이터베이스 URL 반환

        DB_TYPE 환경변수로 데이터베이스 종류를 선택:
        - sqlite (기본값): SQLite 데이터베이스 사용
        - mysql: MySQL 데이터베이스 사용
        """
        if cls.DB_TYPE == "sqlite":
            logger.info(f"SQLite 데이터베이스 사용: {cls.SQLITE_DB_PATH}")
            return f"sqlite+aiosqlite:///{cls.SQLITE_DB_PATH}"
        elif cls.DB_TYPE == "mysql":
            logger.info(f"MySQL 데이터베이스 사용: {cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
            return (
                f"mysql+aiomysql://{cls.DB_USER}:{cls.DB_PASSWORD}"
                f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
                f"?charset=utf8mb4"
            )
        else:
            raise ValueError(f"지원하지 않는 DB_TYPE: {cls.DB_TYPE}. 'sqlite' 또는 'mysql'을 사용하세요.")

    @classmethod
    def get_engine_kwargs(cls) -> dict:
        """엔진 설정 반환 (DB 타입에 따라 다름)"""
        is_development = cls.ENVIRONMENT == "development"
        echo = is_development

        # SQLite 설정
        if cls.DB_TYPE == "sqlite":
            return {
                "echo": echo,
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False}
            }

        # MySQL 설정
        elif cls.DB_TYPE == "mysql":
            if is_development:
                poolclass = NullPool
                pool_kwargs = {}
            else:
                poolclass = QueuePool
                pool_kwargs = {
                    "pool_size": cls.DB_POOL_SIZE,
                    "max_overflow": cls.DB_MAX_OVERFLOW,
                    "pool_timeout": cls.DB_POOL_TIMEOUT,
                    "pool_recycle": cls.DB_POOL_RECYCLE,
                    "pool_pre_ping": True,
                }

            return {
                "echo": echo,
                "poolclass": poolclass,
                **pool_kwargs,
            }

        else:
            raise ValueError(f"지원하지 않는 DB_TYPE: {cls.DB_TYPE}")


engine = create_async_engine(
    DatabaseConfig.get_database_url(),
    **DatabaseConfig.get_engine_kwargs()
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션 의존성"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"데이터베이스 세션 오류: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """데이터베이스 초기화 (개발 환경 전용)"""
    async with engine.begin() as conn:
        if DatabaseConfig.ENVIRONMENT == "development":
            logger.info("데이터베이스 테이블 생성 중...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("데이터베이스 테이블 생성 완료")
        else:
            logger.info("프로덕션 환경: Alembic 마이그레이션 사용 권장")


async def close_db() -> None:
    """데이터베이스 연결 종료"""
    await engine.dispose()
    logger.info("데이터베이스 연결 종료")


async def check_db_connection() -> bool:
    """데이터베이스 연결 확인"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            logger.info("데이터베이스 연결 확인 성공")
            return True
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {str(e)}", exc_info=True)
        return False
