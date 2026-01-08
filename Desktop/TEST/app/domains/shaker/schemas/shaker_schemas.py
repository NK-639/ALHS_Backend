"""Shaker 스키마"""
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


class VialTarget(str, Enum):
    """Vial 타겟 선택"""
    VIAL_1 = "vial_1"
    VIAL_2 = "vial_2"


class ShakerRequest(BaseModel):
    """오비탈 모드용 요청 모델"""
    target: VialTarget = Field(..., description="타겟 위치 (vial_1 또는 vial_2)")
    rpm: int = Field(..., gt=0, description="분당 회전수 (RPM)")
    time_sec: float = Field(..., gt=0, description="쉐이킹 지속 시간 (초)")


class LinearShakerRequest(BaseModel):
    """Linear 모드용 요청 모델"""
    rpm: int = Field(..., gt=0, description="분당 회전수 (RPM)")
    time_sec: float = Field(..., gt=0, description="쉐이킹 지속 시간 (초)")


class ThreeDShakerRequest(BaseModel):
    """3D 모드용 요청 모델"""
    rpm: int = Field(..., gt=0, description="분당 회전수 (RPM)")
    time_sec: float = Field(..., gt=0, description="쉐이킹 지속 시간 (초)")
