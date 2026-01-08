"""사용자 모델"""
from sqlalchemy import Column, String, Boolean
from app.common.models.base import Base


class User(Base):
    """사용자 모델"""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False, index=True)  # 동명이인 허용
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
