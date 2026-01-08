"""사용자 서비스"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.users.models.user import User
from app.domains.users.schemas.user_schemas import UserCreate, UserUpdate, UserResponse
from app.domains.users.repositories.user_repository import UserRepository
from app.utils.transaction import transactional, read_only
from app.exceptions.custom_exceptions import (
    NotFoundException,
    DuplicateResourceException,
    ValidationException
)


class UserService:
    """사용자 비즈니스 로직"""

    def __init__(self):
        self.repository = UserRepository()

    @transactional
    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> UserResponse:
        """사용자 생성 (트랜잭션)"""
        # 이메일 중복 체크 (이메일은 고유해야 함)
        existing_user = await self.repository.get_by_email(db, user_data.email)
        if existing_user:
            raise DuplicateResourceException(
                message="이미 존재하는 이메일입니다",
                field="email",
                detail=f"Email '{user_data.email}' is already registered"
            )

        # 비밀번호 해싱 (실제로는 bcrypt 등을 사용)
        hashed_password = self._hash_password(user_data.password)

        # 사용자 생성
        user = await self.repository.create(db, user_data, hashed_password)
        return UserResponse.model_validate(user)

    @read_only
    async def get_user(self, db: AsyncSession, user_id: int) -> UserResponse:
        """사용자 조회"""
        user = await self.repository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException(
                message="사용자를 찾을 수 없습니다",
                detail=f"User with id {user_id} not found"
            )
        return UserResponse.model_validate(user)

    @read_only
    async def get_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: bool = None
    ) -> List[UserResponse]:
        """사용자 목록 조회"""
        if limit > 100:
            raise ValidationException(
                message="한 번에 최대 100개까지만 조회할 수 있습니다",
                field="limit",
                detail="Limit must be less than or equal to 100"
            )

        users = await self.repository.get_list(db, skip, limit, is_active)
        return [UserResponse.model_validate(user) for user in users]

    @transactional
    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate
    ) -> UserResponse:
        """사용자 정보 수정 (트랜잭션)"""
        user = await self.repository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException(
                message="사용자를 찾을 수 없습니다",
                detail=f"User with id {user_id} not found"
            )

        # 이메일 중복 체크 (변경하는 경우)
        if user_data.email and user_data.email != user.email:
            existing_user = await self.repository.get_by_email(db, user_data.email)
            if existing_user:
                raise DuplicateResourceException(
                    message="이미 존재하는 이메일입니다",
                    field="email"
                )

        # 비밀번호 해싱 (변경하는 경우)
        hashed_password = None
        if user_data.password:
            hashed_password = self._hash_password(user_data.password)

        # 사용자 정보 수정
        updated_user = await self.repository.update(db, user, user_data, hashed_password)
        return UserResponse.model_validate(updated_user)

    @transactional
    async def delete_user(self, db: AsyncSession, user_id: int) -> None:
        """사용자 삭제 (트랜잭션)"""
        user = await self.repository.get_by_id(db, user_id)
        if not user:
            raise NotFoundException(
                message="사용자를 찾을 수 없습니다",
                detail=f"User with id {user_id} not found"
            )

        await self.repository.delete(db, user)

    @staticmethod
    def _hash_password(password: str) -> str:
        """비밀번호 해싱 (예제용 - 실제로는 bcrypt 사용)"""
        # 실제 구현 시에는 passlib의 bcrypt를 사용하세요
        # from passlib.context import CryptContext
        # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # return pwd_context.hash(password)
        return f"hashed_{password}"
