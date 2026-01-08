"""
Klipper/Moonraker API 통신을 담당하는 서비스
"""
import httpx
from app.exceptions import KlipperException


class KlipperService:
    """Klipper API 통신 서비스"""

    def __init__(self, base_url: str = "http://192.168.0.192:7125"):
        self.base_url = base_url
        self.timeout = 30.0

    async def home_printer(self):
        """프린터 초기화 (home)"""
        return await self.send_gcode("G28")

    async def pause_printer(self):
        """프린터 일시정지"""
        return await self.send_gcode("pause")

    async def get_printer_info(self):
        """프린터 정보 조회"""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                response = await client.get("/printer/info")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise KlipperException(
                message="프린터 정보 조회 실패",
                error_code="KLIPPER_HTTP_ERROR",
                detail=f"Klipper 서버 응답 오류: {e.response.status_code} - {e.response.text[:50]}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise KlipperException(
                message="Klipper 서버에 연결할 수 없습니다",
                error_code="KLIPPER_CONNECTION_ERROR",
                detail=f"서버 연결 실패. URL 확인: {self.base_url}",
                status_code=503
            )

    async def send_gcode(self, gcode_script: str):
        """G-code 명령을 Klipper로 전송"""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                response = await client.post(
                    "/printer/gcode/script",
                    json={"script": gcode_script}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            klipper_response_text = e.response.text.strip()
            raise KlipperException(
                message="G-code 명령 전송 실패",
                error_code="KLIPPER_GCODE_ERROR",
                detail=f"Klipper 서버 오류 ({e.response.status_code}): {klipper_response_text}",
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            raise KlipperException(
                message="Klipper 서버에 연결할 수 없습니다",
                error_code="KLIPPER_CONNECTION_ERROR",
                detail=f"서버 연결 실패. URL 확인: {self.base_url}",
                status_code=503
            )
        except KlipperException:
            # KlipperException은 그대로 재발생
            raise
        except Exception as e:
            raise KlipperException(
                message="서버 내부 오류 발생",
                error_code="KLIPPER_INTERNAL_ERROR",
                detail=f"예상치 못한 오류: {type(e).__name__} - {str(e)}",
                status_code=500
            )


