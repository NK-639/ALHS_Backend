"""
FastAPI Shaker Control Application - 메인 진입점

이 파일이 애플리케이션의 진입점입니다.
"""
from fastapi import FastAPI

# FastAPI 앱 인스턴스 생성 (main.py 안에서 직접 정의)
app = FastAPI(
    title="FastAPI Shaker Control",
    description="Shaker 제어 애플리케이션",
    version="1.0.0"
)

# 라우터 등록 (필요한 경우 주석 해제)
# from routers import shaker, run, pause, ws
# app.include_router(shaker.router, prefix="/api/shaker", tags=["shaker"])
# app.include_router(run.router, prefix="/api/run", tags=["run"])
# app.include_router(pause.router, prefix="/api/pause", tags=["pause"])
# app.include_router(ws.router, prefix="/ws", tags=["websocket"])

# app 객체를 직접 export하여 uvicorn이 main:app으로 실행할 수 있도록 함
__all__ = ["app"]
