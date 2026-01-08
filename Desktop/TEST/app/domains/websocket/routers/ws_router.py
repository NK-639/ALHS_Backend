from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websockets.client import connect
from websockets.exceptions import ConnectionClosedOK
import asyncio

# Moonraker 웹소켓 주소 설정
MOONRAKER_WS_URL = "ws://192.168.0.192:7125/websocket"

router = APIRouter(
    prefix="/websocket",
    tags=["WebSocket Proxy"],
)


@router.websocket("")
async def proxy_websocket(client_ws: WebSocket):
    """
    Moonraker 웹소켓 프록시

    - 클라이언트(Mainsail 등)와 Moonraker 사이의 웹소켓 통신을 중계합니다.
    - 양방향 실시간 데이터 전송을 지원합니다.

    Args:
        client_ws: 클라이언트 웹소켓 연결
    """
    # 1. 클라이언트 연결 수락
    await client_ws.accept()
    
    try:
        # 2. Moonraker에 웹소켓 클라이언트 연결
        async with connect(MOONRAKER_WS_URL) as moonraker_ws:
            
            # 3. 클라이언트 -> Moonraker 데이터 중개 함수
            async def client_to_moonraker():
                # 클라이언트 연결이 끊어질 때까지 반복
                while True:
                    data = await client_ws.receive_text()
                    await moonraker_ws.send(data)

            # 4. Moonraker -> 클라이언트 데이터 중개 함수
            async def moonraker_to_client():
                # Moonraker 연결이 끊어질 때까지 반복
                while True:
                    data = await moonraker_ws.recv()
                    await client_ws.send_text(data)

            # 5. 두 중개 함수를 동시에 실행 (병렬 처리)
            # 둘 중 하나라도 종료되면 전체 태스크 종료
            await asyncio.gather(client_to_moonraker(), moonraker_to_client())

    except WebSocketDisconnect:
        # Mainsail/클라이언트가 연결을 끊은 경우
        pass

    except (ConnectionClosedOK, Exception):
        # Moonraker 연결 끊김 또는 그 외 연결 오류 발생 시
        # 프록시 서버는 자동으로 종료 처리됩니다.
        pass

    finally:
        # 연결 종료 시 클라이언트 연결을 안전하게 닫습니다.
        if client_ws.client_state.name == "CONNECTED":
            await client_ws.close()
