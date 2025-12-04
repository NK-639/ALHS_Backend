from fastapi import FastAPI
from routers import run 
from routers import ws
from routers import shaker
from routers import pause
app = FastAPI()

app.include_router(run.router)
app.include_router(pause.router)
app.include_router(ws.router)
app.include_router(shaker.router)

# # ===========================================
# # 3. 실행 방법
# # ===========================================
# # 1. FastAPI와 Uvicorn 설치 (이전에 설치했다면 생략):
# # pip install fastapi "uvicorn[standard]"
# # 2. 터미널 명령어: uvicorn main:app --reload
# # 3. 브라우저에서 http://127.0.0.1:8000/docs 에 접속하여 /run 엔드포인트 테스트.