"""
[모듈] api/app/api/v1.py
[담당] 공통
[역할] 도메인 라우터를 prefix="/api/v1"로 취합하는 단일 진입점.

[구현할 것]
- router: APIRouter
    A 구역 / B 구역에서 각자 자기 도메인 router를 include_router로 등록한다.

[의존]
- 각 도메인 router.py (A: auth/admin/queue/system, B: venue/performance/reservation)

[호출자]
- app.main (create_app에서 prefix="/api/v1"로 include)

[주의]
- registry.py와 마찬가지로 A/B가 공동 수정하는 파일이다. 반드시 자기 구역에만
  줄을 추가할 것. 도메인 순서는 알파벳순으로 고정해 충돌을 최소화한다.
"""

from fastapi import APIRouter

router = APIRouter()

# --- A 구역 (아래에만 추가) ---
from app.domains.admin.router import router as admin_router
from app.domains.auth.router import router as auth_router
from app.domains.member.router import router as member_router
from app.domains.queue.router import router as queue_router
from app.domains.system.router import router as system_router

router.include_router(admin_router)
router.include_router(auth_router)
router.include_router(member_router)
router.include_router(queue_router)
router.include_router(system_router)

# --- B 구역 (아래에만 추가) ---
from app.domains.performance.router import router as performance_router
from app.domains.venue.router import router as venue_router

# from app.domains.reservation.router import router as reservation_router

router.include_router(performance_router)
router.include_router(venue_router)
# router.include_router(reservation_router)
