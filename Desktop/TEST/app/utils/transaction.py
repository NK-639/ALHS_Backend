"""트랜잭션 관리 유틸리티"""
import functools
import logging
from typing import Callable, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def transactional(func: Callable) -> Callable:
    """
    트랜잭션 데코레이터

    자동 커밋/롤백 및 중첩 트랜잭션(SAVEPOINT) 지원
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # 인스턴스 메서드인 경우 args[1]이 db, 일반 함수인 경우 args[0]이 db
        db_index = 1 if len(args) > 1 and isinstance(args[1], AsyncSession) else 0

        if len(args) <= db_index or not isinstance(args[db_index], AsyncSession):
            raise TypeError(
                f"{func.__name__}의 {'두 번째' if db_index == 1 else '첫 번째'} 인자는 AsyncSession이어야 합니다."
            )

        db: AsyncSession = args[db_index]

        if db.in_transaction():
            async with db.begin_nested():
                try:
                    result = await func(*args, **kwargs)
                    logger.debug(f"중첩 트랜잭션 성공: {func.__name__}")
                    return result
                except Exception as e:
                    logger.error(f"중첩 트랜잭션 롤백: {func.__name__} - {str(e)}", exc_info=True)
                    raise
        else:
            try:
                async with db.begin():
                    result = await func(*args, **kwargs)
                    logger.info(f"트랜잭션 커밋 성공: {func.__name__}")
                    return result
            except Exception as e:
                logger.error(f"트랜잭션 롤백: {func.__name__} - {str(e)}", exc_info=True)
                raise

    return wrapper


def read_only(func: Callable) -> Callable:
    """읽기 전용 트랜잭션 데코레이터 (커밋 불필요)"""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # 인스턴스 메서드인 경우 args[1]이 db, 일반 함수인 경우 args[0]이 db
        db_index = 1 if len(args) > 1 and isinstance(args[1], AsyncSession) else 0

        if len(args) <= db_index or not isinstance(args[db_index], AsyncSession):
            raise TypeError(
                f"{func.__name__}의 {'두 번째' if db_index == 1 else '첫 번째'} 인자는 AsyncSession이어야 합니다."
            )

        db: AsyncSession = args[db_index]
        logger.debug(f"읽기 전용 작업: {func.__name__}")

        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"읽기 전용 작업 실패: {func.__name__} - {str(e)}", exc_info=True)
            raise

    return wrapper


class TransactionManager:
    """컨텍스트 매니저를 사용한 명시적 트랜잭션 관리"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.transaction = None

    async def __aenter__(self):
        self.transaction = await self.db.begin()
        logger.debug("트랜잭션 시작 (컨텍스트 매니저)")
        return self.db

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.transaction.rollback()
            logger.error(f"트랜잭션 롤백: {exc_type.__name__} - {exc_val}", exc_info=True)
            return False
        else:
            await self.transaction.commit()
            logger.info("트랜잭션 커밋 성공")
            return True


async def execute_in_transaction(db: AsyncSession, *operations: Callable) -> list:
    """여러 작업을 하나의 트랜잭션으로 실행"""
    results = []

    try:
        async with db.begin():
            for operation in operations:
                result = await operation(db)
                results.append(result)

            logger.info(f"트랜잭션 성공: {len(operations)}개 작업 완료")
            return results

    except Exception as e:
        logger.error(f"트랜잭션 실패: {len(operations)}개 작업 중 에러 - {str(e)}", exc_info=True)
        raise
