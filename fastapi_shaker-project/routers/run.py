from fastapi import APIRouter , HTTPException
from starlette import status # 👈 1. status 모듈 추가
import httpx

router = APIRouter() 

klipper_url = "http://192.168.0.192:7125"
 

@router.get("/run", status_code=200)
async def run():
    """
    shaker 연결 및 실행 예시
    printer/info -> 프린터 정보 조회
    G28 -> 프린터 초기화 (home)
    """
    
    try:
        # 2. httpx.AsyncClient를 async with으로 정의 (가장 중요)
        async with httpx.AsyncClient(base_url=klipper_url, timeout=30.0) as client:
        
            # 1. 프린터 정보 조회 (I/O 작업)
            r_info = await client.get("/printer/info")
            r_info.raise_for_status() # 4xx/5xx 응답 시 예외 발생
            printer_data = r_info.json() 

            print("프린터 정보 조회 완료. homing 시작")

            # 2. 프린터 초기화 (home) (I/O 작업)
            r_home = await client.post(
                "/printer/gcode/script", 
                json={"script": "G28"}
            )
            r_home.raise_for_status() # 4xx/5xx 응답 시 예외 발생
            print("homing 완료. shaker 실행 가능")

            # 👈 최종 응답에 printer_data 포함
            return {
                "message": "shaker 실행 준비 완료",
                # 👈 status.HTTP_200_OK 사용으로 수정
                "status_code": status.HTTP_200_OK, 
                "printer_data": printer_data # <--- 클라이언트에게 이 데이터가 전달됩니다.
            }

    # HTTP 요청/응답 관련 오류만 구체적으로 처리
    except httpx.HTTPStatusError as e:
        # 예: Klipper 서버에서 404나 500 응답이 온 경우
        print(f"HTTP 상태 오류 발생: {e}")
        # 500 Internal Server Error 대신, 적절한 에러 코드를 반환하도록 수정
        raise HTTPException(
            status_code=e.response.status_code, # Klipper 서버에서 받은 상태 코드 사용
            detail=f"Klipper 서버 응답 오류: {e.response.status_code} - {e.response.text[:50]}"
        )
    except httpx.RequestError as e:
        # 예: Klipper 서버 연결이 아예 안 되는 경우 (타임아웃, DNS 오류 등)
        print(f"HTTP 요청 오류 발생 (연결 실패): {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=f"Klipper 서버에 연결할 수 없습니다. URL 확인: {klipper_url}"
        )
    except Exception as e:
        # 위에서 잡지 못한 일반적인 오류
        print(f"예상치 못한 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # 500 상태 코드 사용
            detail=f"서버 내부 오류 발생: {type(e).__name__}"
        )
