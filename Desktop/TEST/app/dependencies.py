"""
의존성 주입(Dependency Injection)을 위한 모듈

FastAPI의 Depends를 활용하여 서비스 인스턴스를 주입합니다.
이를 통해 테스트 용이성과 코드 재사용성을 높입니다.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.printer.services.klipper_service import KlipperService
    from app.domains.shaker.services.shaker_service import ShakerService


def get_klipper_service():
    """
    KlipperService 인스턴스를 반환하는 의존성 함수

    Returns:
        KlipperService: Klipper API 통신 서비스 인스턴스
    """
    from app.domains.printer.services.klipper_service import KlipperService
    return KlipperService(base_url="http://192.168.0.192:7125")


def get_shaker_service():
    """
    ShakerService 인스턴스를 반환하는 의존성 함수

    Returns:
        ShakerService: Shaker G-code 생성 서비스 인스턴스
    """
    from app.domains.shaker.services.shaker_service import ShakerService
    return ShakerService()
