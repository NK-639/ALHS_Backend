"""Shaker 라우터"""
from fastapi import APIRouter, Depends
from starlette import status
from app.domains.shaker.schemas.shaker_schemas import (
    ShakerRequest,
    LinearShakerRequest,
    ThreeDShakerRequest
)
from app.domains.shaker.services.shaker_service import ShakerService
from app.common.schemas import create_success_response
from app.domains.printer.services.klipper_service import KlipperService
from app.dependencies import get_klipper_service
from app.config import get_logger
from app.exceptions import KlipperException

logger = get_logger(__name__)

# Shaker 제어 라우터
router = APIRouter(
    prefix="/shaker",
    tags=["Shaker Control"],
    responses={404: {"description": "Not found"}},
)

shaker_service = ShakerService()


# === Shaker 제어 엔드포인트 ===

@router.post("/orbital")
async def set_orbital_mode(
    req: ShakerRequest,
    klipper_service: KlipperService = Depends(get_klipper_service)
):
    """
    오비탈(원형 궤도) 모드 실행

    - target: vial_1 또는 vial_2 선택
    - 선택한 vial 위치에서 쉐이킹 수행
    """
    # vial 좌표 가져오기
    coords = shaker_service.get_vial_coordinates(req.target.value)
    center_x = coords["x"]
    center_y = coords["y"]

    # Orbital shaking G-code 생성 및 전송 (vial 좌표 기준으로 동작)
    orbital_gcode = shaker_service.generate_orbital_gcode(
        rpm=req.rpm,
        time_sec=req.time_sec,
        center_x=center_x,
        center_y=center_y
    )
    logger.info(f"[ORBITAL] target={req.target.value}, center=({center_x}, {center_y})")
    
    # G-code 전송 시도 (홈 필요 오류 발생 시 자동 홈 수행 후 재시도)
    try:
        moonraker_response = await klipper_service.send_gcode(orbital_gcode)
    except KlipperException as e:
        # "Must home axis first" 오류 확인
        error_detail = e.detail or str(e)
        if "Must home axis first" in error_detail or "must home" in error_detail.lower():
            logger.warning("[ORBITAL] 홈이 필요합니다. 홈 수행 후 재시도합니다.")
            # X, Y축 홈 수행
            await klipper_service.send_gcode("G28 X Y")
            await klipper_service.send_gcode("M400 ; 홈 완료 대기")
            logger.info("[ORBITAL] 홈 완료. G-code 재전송합니다.")
            # 재시도
            moonraker_response = await klipper_service.send_gcode(orbital_gcode)
        else:
            # 다른 오류는 그대로 재발생
            raise
    
    # 동작 완료 후 원점(150, 150)으로 복귀
    home_gcode = shaker_service.generate_home_gcode(home_x=150.0, home_y=150.0)
    logger.info("[ORBITAL] 원점(150, 150)으로 복귀")
    try:
        home_response = await klipper_service.send_gcode(home_gcode)
    except KlipperException as e:
        # 원점 복귀 시에도 홈 필요 오류 발생 가능
        error_detail = e.detail or str(e)
        if "Must home axis first" in error_detail or "must home" in error_detail.lower():
            logger.warning("[ORBITAL] 원점 복귀 시 홈이 필요합니다. 홈 수행 후 재시도합니다.")
            await klipper_service.send_gcode("G28 X Y")
            await klipper_service.send_gcode("M400 ; 홈 완료 대기")
            home_response = await klipper_service.send_gcode(home_gcode)
        else:
            raise

    return create_success_response(
        message="오비탈 모드 동작 실행 완료",
        data={
            "parameters": {
                "target": req.target.value,
                "rpm": req.rpm,
                "duration_sec": req.time_sec,
                "coordinates": coords
            },
            "gcode_lines": len(orbital_gcode.splitlines()),
            "moonraker_response": moonraker_response,
            "home_response": home_response,
            "home_position": {"x": 150.0, "y": 150.0}
        }
    )


@router.post("/linear")
async def set_linear_mode(
    req: LinearShakerRequest,
    klipper_service: KlipperService = Depends(get_klipper_service)
):
    """
    리니어(직선 왕복) 모드 실행

    - Y축을 따라 직선 왕복 운동을 수행하는 쉐이킹 모드입니다.
    - RPM과 지속 시간을 설정할 수 있습니다.
    """
    gcode_script = shaker_service.generate_linear_gcode(
        rpm=req.rpm,
        time_sec=req.time_sec
    )
    moonraker_response = await klipper_service.send_gcode(gcode_script)

    return create_success_response(
        message="linear 모드 동작 실행 완료",
        data={
            "parameters": {
                "rpm": req.rpm,
                "duration_sec": req.time_sec
            },
            "moonraker_response": moonraker_response
        }
    )


@router.post("/3d")
async def set_3d_mode(
    req: ThreeDShakerRequest,
    klipper_service: KlipperService = Depends(get_klipper_service)
):
    """
    3D (헬리컬 와블링) 모드 실행

    - X, Y축은 원형 궤도를, Z축은 사인파 왕복 운동을 수행합니다.
    - 3차원 공간에서 복합적인 쉐이킹 효과를 제공합니다.
    """
    gcode_script = shaker_service.generate_3d_gcode(
        rpm=req.rpm,
        time_sec=req.time_sec
    )
    moonraker_response = await klipper_service.send_gcode(gcode_script)

    return create_success_response(
        message="3D 모드 동작 실행 완료",
        data={
            "parameters": {
                "rpm": req.rpm,
                "duration_sec": req.time_sec,
                **shaker_service.get_3d_parameters()
            },
            "moonraker_response": moonraker_response
        }
    )
