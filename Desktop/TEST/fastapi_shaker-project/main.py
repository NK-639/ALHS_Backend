"""
FastAPI Shaker Control Application - Railway 배포용 엔트리 포인트

Railway 배포 시 이 파일이 진입점이 됩니다.
실제 애플리케이션 로직은 app/main.py에 있습니다.
"""
from app.main import app

# app 객체를 직접 export하여 uvicorn이 main:app으로 실행할 수 있도록 함
__all__ = ["app"]
