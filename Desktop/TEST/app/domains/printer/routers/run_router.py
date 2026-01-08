from fastapi import APIRouter, Depends
from starlette import status
from app.domains.printer.services.klipper_service import KlipperService
from app.dependencies import get_klipper_service
from app.config import get_logger
from app.common.schemas import create_success_response

logger = get_logger(__name__)

router = APIRouter(
    prefix="/printer",
    tags=["Printer Control"],
    responses={404: {"description": "Not found"}},
)


@router.get("/run", status_code=status.HTTP_200_OK)
async def run_printer(
    klipper_service: KlipperService = Depends(get_klipper_service)
):
    """
    프린터 실행 준비

    - 프린터 정보를 조회하고 초기화(homing)를 수행합니다.
    - G28 명령으로 프린터를 홈 위치로 이동시킵니다.

    Returns:
        dict: 프린터 정보 및 실행 준비 완료 메시지
    """
    # 1. 프린터 정보 조회
    printer_data = await klipper_service.get_printer_info()
    logger.info("프린터 정보 조회 완료. homing 시작")

    # 2. 프린터 초기화 (home)
    await klipper_service.home_printer()
    logger.info("homing 완료. shaker 실행 가능")

    return create_success_response(
        message="shaker 실행 준비 완료",
        data={"printer_data": printer_data}
    )
