"""
[모듈] api/app/domains/system/router.py
[담당] A
[역할] /health/live(프로세스 생존), /health/ready(DB+Valkey 각 1초 타임아웃 체크)

[구현할 것]
- GET /health/live -> 200
- GET /health/ready -> DB·Valkey 중 하나만 죽어도 503

[의존]
- app.domains.system.service

[호출자]
- app.api.v1
"""

from fastapi import APIRouter, HTTPException

from app.domains.system import service as system_service

router = APIRouter(tags=["system"])


@router.get("/health/live")
def health_live() -> dict:
    return {"status": "ok"}


@router.get("/health/ready")
def health_ready() -> dict:
    db_ok = system_service.check_db()
    cache_ok = system_service.check_cache()
    if not (db_ok and cache_ok):
        raise HTTPException(status_code=503, detail={"db": db_ok, "cache": cache_ok})
    return {"status": "ready", "db": db_ok, "cache": cache_ok}
