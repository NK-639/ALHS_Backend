from fastapi import APIRouter , HTTPException
from starlette import status
import httpx

router = APIRouter() 

klipper_url = "http://192.168.0.192:7125"

"""
동작 정지 엔드포인트  : pause 명령 실행
"""

@router.post("/pause", status_code=200)
async def pause(): 
    """
    pause 명령을 Klipper 서버에 전송하고, 
    성공 시 'shaker 동작 정지 완료' 메시지를 반환.
    """
    # 전송할 스크립트를 'pause'로 하드코딩 (긴급 정지 명령)
    gcode_script = "pause"
    
    try:
        async with httpx.AsyncClient(base_url=klipper_url) as client:
            r_stop = await client.post(
                "/printer/gcode/script", 
                # 전송할 JSON 데이터에 하드코딩된 M112 사용
                json={"script": gcode_script} 
            )
            r_stop.raise_for_status() # 4xx/5xx 응답 시 예외 발생
            
            # 성공 시 즉시 '동작 정지 완료' 메시지 반환
            return {
                "message": "printer 동작 정지 완료", 
                "status_code": status.HTTP_200_OK
            }
            
    except httpx.HTTPStatusError as e:
        klipper_response_text = e.response.text.strip()
        print(f"HTTP 상태 오류 발생: {e} / Klipper 응답: {klipper_response_text}")
        
        raise HTTPException(
            status_code=e.response.status_code,
            # 응답 상태 코드와 Klipper가 보낸 상세 메시지를 함께 보여줍니다.
            detail=f"Klipper 서버 오류 ({e.response.status_code}): {klipper_response_text}"
        )
        
    except httpx.RequestError as e:
        # Klipper 서버 연결 실패 처리
        print(f"HTTP 요청 오류 발생 (연결 실패): {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Klipper 서버에 연결할 수 없습니다. URL 확인: {klipper_url} (네트워크 및 Klipper 상태 확인 필요)"
        )
        
    except Exception as e:
        # 기타 내부 오류 처리
        print(f"예상치 못한 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 내부 오류 발생: {type(e).__name__} - {e}"
        )