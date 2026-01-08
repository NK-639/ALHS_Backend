"""사용자 리포지토리"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.users.models.user import User
from app.domains.users.schemas.user_schemas import UserCreate, UserUpdate


class UserRepository:
    """사용자 리포지토리 (데이터베이스 접근 계층)"""

    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate, hashed_password: str) -> User:
        """사용자 생성"""
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """사용자명으로 조회"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """사용자 목록 조회"""
        query = select(User)

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, user: User, user_data: UserUpdate, hashed_password: Optional[str] = None) -> User:
        """사용자 정보 수정"""
        if user_data.email is not None:
            user.email = user_data.email
        if user_data.username is not None:
            user.username = user_data.username
        if hashed_password is not None:
            user.hashed_password = hashed_password
        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete(db: AsyncSession, user: User) -> None:
        """사용자 삭제"""
        await db.delete(user)
        await db.flush()
