FROM python:3.11-slim

# 작업 폴더 설정
WORKDIR /app

# 1. 필수 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 소스 코드 전체 복사 (중요: app 폴더가 아니라 점(.)을 찍어서 현재 폴더 전체를 복사)
COPY . .

# 3. 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
