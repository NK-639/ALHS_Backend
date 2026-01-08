"""
FastAPI Shaker Control Application

도메인 기반 아키텍처로 구성된 Klipper/Moonraker 기반 Shaker 제어 애플리케이션입니다.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime, date
from pathlib import Path

from app.domains.users import router as users_router
from app.domains.printer import run_router
from app.domains.shaker import router as shaker_router
from app.domains.websocket import router as ws_router
from app.config import LogConfig, get_logger
from app.config.database import init_db, close_db
from app.middleware import LoggingMiddleware, setup_cors_middleware
from app.handlers import setup_exception_handlers
from app.common.schemas import create_success_response

# 모델 import (SQLAlchemy가 테이블을 생성하기 위해 필요)
from app.domains.users.models import User  # noqa: F401

# 로깅 설정 초기화
LogConfig.setup_logging()
logger = get_logger(__name__)

# ========================================
# Pydantic Schema 정의
# ========================================
class ReservationRequest(BaseModel):
    """예약 요청 스키마"""
    user_name: str = Field(..., description="사용자 이름", min_length=1)
    equipment_type: Literal["large", "small"] = Field(..., description="장비 타입 (large/small)")
    start_time: str = Field(..., description="시작 시간 (HH:MM 형식)", pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., description="종료 시간 (HH:MM 형식)", pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")

    class Config:
        json_schema_extra = {
            "example": {
                "user_name": "김나경",
                "equipment_type": "large",
                "start_time": "18:00",
                "end_time": "19:00"
            }
        }


class UsageLog(BaseModel):
    """사용 로그 스키마"""
    id: int
    equipment_type: str
    user_name: str
    date: str
    start_time: str
    end_time: str
    duration_hours: int
    duration_minutes: int

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "equipment_type": "large",
                "user_name": "이소연",
                "date": "2026-01-07",
                "start_time": "12:58",
                "end_time": "17:59",
                "duration_hours": 5,
                "duration_minutes": 1
            }
        }


# ========================================
# 메모리 기반 더미 DB (실제 DB로 교체 가능)
# ========================================
# 사용 로그를 저장하는 메모리 리스트
usage_logs: List[dict] = []
log_id_counter = 1

# 초기 샘플 데이터 추가
usage_logs.append({
    "id": log_id_counter,
    "equipment_type": "large",
    "user_name": "이소연",
    "date": "2026-01-07",
    "start_time": "12:58",
    "end_time": "17:59",
    "duration_hours": 5,
    "duration_minutes": 1
})
log_id_counter += 1


# ========================================
# FastAPI 애플리케이션 설정
# ========================================
app = FastAPI(
    title="Shaker Control API",
    description="Klipper/Moonraker 기반 Shaker 제어 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ========================================
# 예외 핸들러 설정
# ========================================
# 예외 핸들러 등록 (미들웨어보다 먼저 설정)
setup_exception_handlers(app)

# ========================================
# 미들웨어 설정
# ========================================
# CORS 미들웨어 설정 (프로덕션에서는 allow_development=False로 변경)
setup_cors_middleware(app, allow_development=True)

# 로깅 미들웨어 추가
app.add_middleware(LoggingMiddleware)

# ========================================
# 정적 파일 마운트
# ========================================
# static 폴더 경로 설정
# Railway 배포 시: Root Directory가 /fastapi_shaker-project이고 app/ 폴더가 복사되면
# static/ 폴더는 /app/static/에 있음 (app/main.py의 상위 디렉토리)
# 로컬 개발 시: app/main.py에서 상위 디렉토리의 fastapi_shaker-project/static/ 참조
static_dir = Path(__file__).parent.parent / "fastapi_shaker-project" / "static"
# Railway 배포 환경에서는 static/ 폴더가 app/ 폴더와 같은 레벨에 있음
if not static_dir.exists():
    static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"📁 정적 파일 마운트: {static_dir}")
else:
    logger.warning(f"⚠️  정적 파일 디렉토리를 찾을 수 없습니다: {static_dir}")

# ========================================
# 라우터 등록
# ========================================
# Users 도메인 (예제 CRUD)
app.include_router(users_router)

# Printer 도메인 (프린터 제어)
app.include_router(run_router)


# Shaker 도메인 (Shaker 제어)
app.include_router(shaker_router)

# WebSocket 도메인 (실시간 통신)
app.include_router(ws_router)


# ========================================
# 이벤트 핸들러
# ========================================
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("🚀 Shaker Control API 서버 시작")
    await init_db()
    logger.info("📖 API 문서: http://127.0.0.1:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    await close_db()
    logger.info("🛑 Shaker Control API 서버 종료")


# ========================================
# 루트 엔드포인트 - HTML 파일 반환
# ========================================
@app.get("/", tags=["Web"])
async def root():
    """
    메인 페이지 (index.html)

    Returns:
        FileResponse: index.html 파일
    """
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        raise HTTPException(status_code=404, detail="index.html을 찾을 수 없습니다.")


# ========================================
# SpeedVac 예약 API 엔드포인트
# ========================================
@app.post("/api/reservations", tags=["SpeedVac"])
async def create_reservation(request: ReservationRequest):
    """
    SpeedVac 예약 생성

    Args:
        request: 예약 요청 데이터 (사용자명, 장비타입, 시작시간, 종료시간)

    Returns:
        dict: 생성된 예약 정보
    """
    global log_id_counter
    
    # 시간 차이 계산
    start_dt = datetime.strptime(request.start_time, "%H:%M")
    end_dt = datetime.strptime(request.end_time, "%H:%M")
    
    # 종료 시간이 시작 시간보다 작으면 다음 날로 간주
    if end_dt < start_dt:
        end_dt = datetime.strptime(f"2000-01-02 {request.end_time}", "%Y-%m-%d %H:%M")
        start_dt = datetime.strptime(f"2000-01-01 {request.start_time}", "%Y-%m-%d %H:%M")
    else:
        end_dt = datetime.strptime(f"2000-01-01 {request.end_time}", "%Y-%m-%d %H:%M")
        start_dt = datetime.strptime(f"2000-01-01 {request.start_time}", "%Y-%m-%d %H:%M")
    
    diff = end_dt - start_dt
    total_seconds = int(diff.total_seconds())
    duration_hours = total_seconds // 3600
    duration_minutes = (total_seconds % 3600) // 60
    
    # 로그 데이터 생성
    log_entry = {
        "id": log_id_counter,
        "equipment_type": request.equipment_type,
        "user_name": request.user_name,
        "date": date.today().isoformat(),
        "start_time": request.start_time,
        "end_time": request.end_time,
        "duration_hours": duration_hours,
        "duration_minutes": duration_minutes
    }
    
    # 메모리 DB에 추가 (최신순으로 유지하기 위해 앞에 추가)
    usage_logs.insert(0, log_entry)
    log_id_counter += 1
    
    logger.info(f"✅ 예약 생성: {request.user_name} - {request.equipment_type} ({request.start_time} ~ {request.end_time})")
    
    return create_success_response(
        message="예약이 성공적으로 생성되었습니다.",
        data=log_entry
    )


@app.get("/api/logs", tags=["SpeedVac"])
async def get_logs():
    """
    사용 로그 조회 (최신순)

    Returns:
        dict: 사용 로그 리스트
    """
    # 최신순으로 정렬 (이미 insert(0)로 최신이 앞에 있지만 확실히 하기 위해)
    sorted_logs = sorted(usage_logs, key=lambda x: (x["date"], x["start_time"]), reverse=True)
    
    return create_success_response(
        message="로그 조회 성공",
        data=sorted_logs
    )


@app.delete("/api/logs", tags=["SpeedVac"])
async def delete_all_logs():
    """
    모든 사용 로그 삭제

    Returns:
        dict: 삭제 결과
    """
    global usage_logs, log_id_counter
    
    deleted_count = len(usage_logs)
    usage_logs.clear()
    log_id_counter = 1
    
    logger.info(f"🗑️  모든 로그 삭제: {deleted_count}개")
    
    return create_success_response(
        message=f"{deleted_count}개의 로그가 삭제되었습니다.",
        data={"deleted_count": deleted_count}
    )


# ========================================
# Health Check 엔드포인트
# ========================================
@app.get("/health", tags=["Health"])
async def health_check():
    """
    헬스 체크 엔드포인트

    Returns:
        dict: 서버 상태
    """
    return create_success_response(
        message="서버가 정상 작동 중입니다",
        data={"status": "ok"}
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """
    헬스 체크 엔드포인트

    Returns:
        dict: 서버 상태
    """
    return create_success_response(
        message="서버가 정상 작동 중입니다",
        data={"status": "ok"}
    )


# ===========================================
# 실행 방법
# ===========================================
# 1. 의존성 설치:
#    pip install -r requirements.txt
#
# 2. 개발 서버 실행:
#    uvicorn app.main:app --reload
#
# 3. API 문서 확인:
#    http://127.0.0.1:8000/docs
