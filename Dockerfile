# Python 3.11 슬림 버전 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# build.sh 스크립트 실행 (상위 디렉토리의 app/ 폴더를 현재 디렉토리로 복사)
# Railway 빌드 시 build.sh가 실행되어 app/ 폴더가 복사됨
# app/ 폴더 복사 (build.sh에 의해 복사됨)
COPY app ./app

# static 폴더 복사 (현재 fastapi_shaker-project/static에 있음)
COPY static ./static

# main.py 복사 (fastapi_shaker-project/main.py)
COPY main.py .

# 포트 노출
EXPOSE 8000

# 실행 커맨드
# Railway에서 Root Directory가 /fastapi_shaker-project이고
# main.py가 /app/main.py에 있으므로 main:app으로 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
