"""
[모듈] api/app/domains/system/router.py
[담당] A
[역할] /health/live(Liveness), /health/ready(Readiness), /version(앱/API 버전 조회).
       api 설계서 SYS-001/002/003에 대응.

[구현할 것]
- GET /health/live -> { status: "UP" }
- GET /health/ready -> DB·Valkey 중 하나만 죽어도 503, { status, checks: { db, valkey } }
- GET /version?platform= -> VersionResponse

[의존]
- app.domains.system.service

[호출자]
- app.api.v1
"""

from fastapi import APIRouter, HTTPException

from app.domains.system import service as system_service
from app.domains.system.schema import VersionResponse

router = APIRouter(tags=["system"])


@router.get("/health/live")
def health_live() -> dict:
    return {"status": "UP"}


@router.get("/health/ready")
def health_ready() -> dict:
    db_ok = system_service.check_db()
    cache_ok = system_service.check_cache()
    checks = {"db": "UP" if db_ok else "DOWN", "valkey": "UP" if cache_ok else "DOWN"}

    if not (db_ok and cache_ok):
        raise HTTPException(status_code=503, detail={"status": "DOWN", "checks": checks})
    return {"status": "UP", "checks": checks}


@router.get("/version", response_model=VersionResponse)
def get_version(platform: str | None = None) -> VersionResponse:
    info = system_service.get_version_info(platform)
    return VersionResponse(**info)
