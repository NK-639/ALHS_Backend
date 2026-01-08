"""사용자 라우터"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db
from app.domains.users.services.user_service import UserService
from app.domains.users.schemas.user_schemas import UserCreate, UserUpdate, UserResponse
from app.common.schemas import create_success_response

router = APIRouter(prefix="/users", tags=["users"])
service = UserService()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="사용자 생성"
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 사용자를 생성합니다.

    - **email**: 이메일 주소 (중복 불가)
    - **username**: 사용자명 (중복 불가, 3-100자)
    - **password**: 비밀번호 (8자 이상)
    """
    user = await service.create_user(db, user_data)
    return create_success_response(
        message="사용자가 생성되었습니다",
        data=user.model_dump()
    )


@router.get(
    "",
    summary="사용자 목록 조회"
)
async def get_users(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="조회할 개수"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 목록을 조회합니다.

    - **skip**: 건너뛸 개수 (페이지네이션)
    - **limit**: 조회할 개수 (최대 100)
    - **is_active**: 활성 상태 필터 (true/false/null)
    """
    users = await service.get_users(db, skip, limit, is_active)
    return create_success_response(
        message=f"{len(users)}명의 사용자를 조회했습니다",
        data=[user.model_dump() for user in users]
    )


@router.get(
    "/{user_id}",
    summary="사용자 단건 조회"
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """특정 사용자의 정보를 조회합니다."""
    user = await service.get_user(db, user_id)
    return create_success_response(
        message="사용자 정보를 조회했습니다",
        data=user.model_dump()
    )


@router.patch(
    "/{user_id}",
    summary="사용자 정보 수정"
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 정보를 수정합니다.

    - 수정하고 싶은 필드만 전송하면 됩니다
    - 전송하지 않은 필드는 기존 값을 유지합니다
    """
    user = await service.update_user(db, user_id, user_data)
    return create_success_response(
        message="사용자 정보가 수정되었습니다",
        data=user.model_dump()
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="사용자 삭제"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """사용자를 삭제합니다."""
    await service.delete_user(db, user_id)
    return create_success_response(
        message="사용자가 삭제되었습니다",
        data=None
    )
