"""
FastAPI Shaker Control Application - Railway 배포용 엔트리 포인트

Railway 배포 시 이 파일이 진입점이 됩니다.
"""
from fastapi import FastAPI

# 🚨 'from app.main import app' 이 부분은 반드시 지우세요!
app = FastAPI()  # <--- 이렇게 main.py 안에서 app이 정의되어 있어야 합니다.

# app 객체를 직접 export하여 uvicorn이 main:app으로 실행할 수 있도록 함
__all__ = ["app"]
