from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
import numpy as np

router = APIRouter()
MOONRAKER_URL = "http://192.168.0.192:7125"

# 💡 쉐이커 상수 (파일 최상단에 정의 유지)
ORBITAL_RADIUS_MM = 5.0
CENTER_X = 150.0
CENTER_Y = 150.0
CENTER_Z = 10.0

# 💡 3D 모드 고정 파라미터 추가
FIXED_ORBITAL_RADIUS_3D = 10.0 # 3D 모드에서 사용할 고정 XY 궤도 반지름 (mm)
FIXED_AMPLITUDE_Z_3D = 5.0    # 3D 모드에서 사용할 고정 Z축 진폭 (mm)

# 🚨 필수 추가: Klipper Z축 최대 속도 (15 mm/s * 60)
MAX_Z_FEEDRATE_MM_MIN = 900.0

## --- 1. Pydantic 모델 정의 ---

class ShakerRequest(BaseModel):
    """오비탈 모드용 요청 모델 (RPM, 시간 + 고정 상수 정보 포함)"""
    rpm: int = Field(..., gt=0, description="분당 회전수 (RPM)")
    time_sec: float = Field(..., gt=0, description="쉐이킹 지속 시간 (초)")


class LinearShakerRequest(BaseModel): # 👈 Linear 모드 전용 모델
    """Linear 모드용 요청 모델: RPM과 시간만 포함"""
    rpm: int = Field(..., gt=0, description="분당 회전수 (RPM)")
    time_sec: float = Field(..., gt=0, description="쉐이킹 지속 시간 (초)")

class ThreeDShakerRequest(BaseModel): 
    """3D 모드용 요청 모델: RPM과 시간만 포함"""
    rpm: int = Field(..., gt=0, description="분당 회전수 (RPM)")
    time_sec: float = Field(..., gt=0, description="쉐이킹 지속 시간 (초)")

## --- 2. Moonraker 통신 함수 ---

async def send_gcode_to_moonraker(gcode_script: str):
    """Moonraker API를 통해 Klipper로 G-Code를 전송하는 비동기 함수"""
    script_endpoint = f"{MOONRAKER_URL}/printer/gcode/script"
    payload = {"script": gcode_script}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(script_endpoint, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Moonraker 연결 오류 또는 타임아웃: {e}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"Moonraker 응답 오류. Moonraker 메시지: {e.response.text}"
        )


## --- 3. G-code 생성 함수 ---

def generate_orbital_gcode(rpm: int, time_sec: float) -> str:
    """ORBITAL 모드 G-code 시퀀스 생성 함수"""
    # 전역 상수를 지역 변수로 복사 (Python 스코프 문제 방지)
    amplitude_mm = ORBITAL_RADIUS_MM
    center_x = CENTER_X
    center_y = CENTER_Y

    # ... (기존 orbital 로직은 변경 없음)
    rps = rpm / 60.0
    omega = rps * 2 * np.pi 
    calculated_speed_f = (2 * np.pi * amplitude_mm * rps) * 60 
    speed_f = max(2000, calculated_speed_f) 
    steps_per_sec = 50
    num_steps = int(time_sec * steps_per_sec)
    time_points = np.linspace(0, time_sec, num_steps, endpoint=False)
    
    gcode_commands = []
    gcode_commands.append("G21 ; 단위를 mm로 설정")
    gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} F6000 ; 중심 좌표로 이동")
    
    for t in time_points:
        x = amplitude_mm * np.cos(omega * t) + center_x
        y = amplitude_mm * np.sin(omega * t) + center_y
        gcode_commands.append(f"G1 X{x:.4f} Y{y:.4f} F{int(speed_f)}") 
    
    gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} F6000 ; 중심 좌표로 복귀")
    gcode_commands.append("M400 ; 모든 이동이 완료될 때까지 기다립니다. (안정성 확보)")
    gcode_commands.append(f"G92 X{center_x:.4f} Y{center_y:.4f} ; 현재 위치를 중심 좌표로 재설정")
    
    return "\n".join(gcode_commands)

def generate_linear_gcode(rpm: int, time_sec: float) -> str:
    """
    LINEAR 모드 G-code 시퀀스 생성 함수 (시간 기반 경로)
    """
    center_x = CENTER_X
    center_y = CENTER_Y
    amplitude_y = 25.0
    
    # 🚨 수정: 시간 기반 경로 생성 설정
    rps = rpm / 60.0 # 초당 왕복 횟수 (주파수)
    omega = rps * 2 * np.pi 
    
    # 왕복 운동 거리(50mm)를 1초에 rps만큼 왕복하는 데 필요한 선형 속도
    calculated_speed_f = (4 * amplitude_y * rps) * 60 # 4 * A * RPS * 60
    speed_f = max(2000, calculated_speed_f)

    # 🚨 수정: steps_per_sec을 orbital과 동일하게 50으로 복원
    steps_per_sec = 50 
    num_steps = int(time_sec * steps_per_sec)
    time_points = np.linspace(0, time_sec, num_steps, endpoint=False)
    
    gcode_commands = []
    gcode_commands.append("G21 ; 단위를 mm로 설정")
    gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} F6000 ; 중심 좌표로 이동")

    for t in time_points:
        # 🚨 새로운 로직: 사인파를 사용하여 Y축 왕복 운동을 시간에 따라 부드럽게 생성
        # Y = A * sin(wt) + CenterY
        y = amplitude_y * np.sin(omega * t) + center_y
        x = center_x # X축은 고정

        gcode_commands.append(f"G1 X{x:.4f} Y{y:.4f} F{int(speed_f)}") 

    # 종료 및 정지 명령은 유지
    gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} F6000 ; 중심 좌표로 복귀")
    gcode_commands.append("M400 ; 모든 이동이 완료될 때까지 기다립니다. (안정성 확보)")
    gcode_commands.append(f"G92 X{center_x:.4f} Y{center_y:.4f} ; 현재 위치를 중심 좌표로 재설정")
    
    return "\n".join(gcode_commands)

def generate_3d_gcode(rpm: int, time_sec: float) -> str:
    """
    3D (헬리컬 와블링) 모드 G-code 시퀀스 생성 함수
    
    X, Y는 원형 궤도를 돌고, Z는 X/Y와 동기화된 사인파 왕복 운동을 수행합니다.
    """
    center_x = CENTER_X
    center_y = CENTER_Y
    center_z = CENTER_Z
    amplitude_xy = FIXED_ORBITAL_RADIUS_3D
    amplitude_z = FIXED_AMPLITUDE_Z_3D
    
    # Z축 진폭의 절반 (중심으로부터의 최대 이동 거리)
    amplitude_z_half = amplitude_z / 2.0 

    # 수학적 경로 계산 설정
    rps = rpm / 60.0
    omega = rps * 2 * np.pi
    
    # 1. XY 평면 회전에 필요한 Feedrate 계산 (mm/min)
    calculated_speed_xy = (2 * np.pi * amplitude_xy * rps) * 60
    
    # 2. 최종 Feedrate 결정 (Klipper Z축 최대 속도 제한 적용)
    # final_feedrate는 XY 속도와 Klipper Z축 최대 속도(900 mm/min) 중 작은 값으로 제한합니다.
    final_feedrate = min(calculated_speed_xy, MAX_Z_FEEDRATE_MM_MIN)
    final_feedrate = max(2000, final_feedrate) 

    # 3. G-code 해상도 (시간 정확도 확보)
    steps_per_sec = 50 
    num_steps = int(time_sec * steps_per_sec)
    time_points = np.linspace(0, time_sec, num_steps, endpoint=False)
    
    gcode_commands = []
    
    # 1. 초기화 및 시작 위치 이동
    # G28 (호밍) 명령 제거. G21 명령만 실행.
    gcode_commands.append("G21 ; 단위를 mm로 설정")
    # 시작 위치를 중심 좌표 (CENTER_Z)로 빠르게 이동
    gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} Z{center_z:.4f} F6000 ; 중심 좌표로 이동") 

    # 2. 경로 계산 및 G1 명령 생성
    for t in time_points:
        # X, Y: 원형 궤적 (오비탈)
        x = amplitude_xy * np.cos(omega * t) + center_x
        y = amplitude_xy * np.sin(omega * t) + center_y
        
        # 🚨 Z: X/Y와 동기화된 사인파 왕복 운동 (Z축 와블링 구현)
        # Z축은 CENTER_Z를 중심으로 ±(amplitude_z/2)만큼 주기적으로 움직입니다.
        z = amplitude_z_half * np.sin(omega * t) + center_z 
        
        gcode_commands.append(f"G1 X{x:.4f} Y{y:.4f} Z{z:.4f} F{int(final_feedrate)}") 

    # 3. 종료 및 정지 명령
    gcode_commands.append(f"G0 X{center_x:.4f} Y{center_y:.4f} Z{center_z:.4f} F6000 ; 중심 좌표로 복귀")
    gcode_commands.append("M400 ; 모든 이동이 완료될 때까지 기다립니다. (안정성 확보)")
    gcode_commands.append(f"G92 X{center_x:.4f} Y{center_y:.4f} Z{center_z:.4f} ; 현재 위치를 중심 좌표로 재설정")
    
    return "\n".join(gcode_commands)
## --- 4. FastAPI 엔드포인트 ---

@router.post("/orbital") 
async def set_orbital_mode(req: ShakerRequest):
    """오비탈 모드 동작 실행 엔드포인트"""
    # 1. G-code 시퀀스 생성
    gcode_script = generate_orbital_gcode(
        rpm=req.rpm,
        time_sec=req.time_sec
    )
    
    # 2. Moonraker에 비동기로 전송 및 응답 받기
    moonraker_response = await send_gcode_to_moonraker(gcode_script)
    
    return {
        "message": "오비탈 모드 동작 실행 완료",
        "parameters": {
            "rpm": req.rpm,
            "duration_sec": req.time_sec,
            "fixed_radius_mm": ORBITAL_RADIUS_MM, # 전역 상수 사용
            "center_xy": (CENTER_X, CENTER_Y)    # 전역 상수 사용
        },
        "moonraker_response": moonraker_response
    }

@router.post("/linear")
async def set_linear_mode(req: LinearShakerRequest): # 👈 LinearShakerRequest 사용
    """linear 모드 동작 실행 엔드포인트"""

    gcode_script = generate_linear_gcode(
        rpm=req.rpm,
        time_sec=req.time_sec
    )
    moonraker_response = await send_gcode_to_moonraker(gcode_script)
    return {
        "message": "linear 모드 동작 실행 완료",
        "parameters": {
            "rpm": req.rpm,
            "duration_sec": req.time_sec
        },
        "moonraker_response": moonraker_response
    }

"""
3D 모드 동작 실행 엔드포인트
"""
@router.post("/3d")
async def set_3d_mode(req: ThreeDShakerRequest):
    """
    3D (헬리컬) 모드 동작 실행 엔드포인트
    """
    # 1. G-code 시퀀스 생성
    # 🚨 수정: generate_3d_gcode 함수 시그니처에 맞게 rpm과 time_sec만 전달합니다.
    gcode_script = generate_3d_gcode(
        rpm=req.rpm,
        time_sec=req.time_sec
        # orbital_radius_mm=req.orbital_radius_mm,  <-- 이 두 줄을 제거해야 합니다.
        # amplitude_z_mm=req.amplitude_z_mm        <-- 이 두 줄을 제거해야 합니다.
    )
    
    # 2. Moonraker에 비동기로 전송 및 응답 받기
    moonraker_response = await send_gcode_to_moonraker(gcode_script)
    return {
        "message": "3D 모드 동작 실행 완료",
        "parameters": {
            "rpm": req.rpm,
            "duration_sec": req.time_sec,
            # 응답 파라미터는 전역 상수를 사용하여 올바르게 유지됩니다.
            "orbital_radius_mm": FIXED_ORBITAL_RADIUS_3D, 
            "amplitude_z_mm": FIXED_AMPLITUDE_Z_3D,
            "center_xyz": (CENTER_X, CENTER_Y, CENTER_Z)
        },
        "moonraker_response": moonraker_response
    }