"""
[모듈] api/app/workers/hold_sweeper.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] TTL 만료된 좌석 Hold를 주기적으로 찾아 좌석을 AVAILABLE로 복구.

[구현할 것]
- sweep_expired_holds(db) -> int (되돌린 hold 개수)
- run() -> None (리더일 때만 무한 루프)

[의존]
- app.workers.base (리더 선출, A가 구현)
- app.domains.reservation.repository (get_expired_holding_holds)
- app.domains.reservation.hold_service (expire_hold — Valkey 락 해제 + DB 갱신 + 캐시 무효화)
- app.db.session (WriterSessionLocal — FastAPI 요청 밖이라 get_db Depends를 못 씀)

[호출자]
- systemd (sesac-hold-sweeper.service, queue_dispatcher와 동일한 배포 방식)

[주의]
- Valkey의 seat:lock:{scheduleSeatId} 키 자체도 hold_seats.lua가 HOLD_TTL_SEC로
  TTL을 걸어두므로 대부분 자연 만료되지만, DB(schedule_seat.status/seat_hold_log)는
  누군가 명시적으로 되돌리지 않으면 영원히 HELD/HOLDING으로 남는다. 이 워커가 그
  DB 쪽 정리를 담당한다.
- 각 tick마다 새 writer 세션을 열고 닫는다 — 장시간 유지되는 세션을 피하기 위함.
"""

import logging
from datetime import datetime

from app.core.config import get_settings
from app.db.session import WriterSessionLocal
from app.domains.reservation import repository
from app.domains.reservation.hold_service import expire_hold
from app.workers.base import run_as_leader

logger = logging.getLogger(__name__)


def sweep_expired_holds(db) -> int:
    expired_holds = repository.get_expired_holding_holds(db, now=datetime.now())
    for hold_log in expired_holds:
        expire_hold(db, hold_log)
    return len(expired_holds)


def _tick() -> None:
    db = WriterSessionLocal()
    try:
        swept = sweep_expired_holds(db)
        if swept:
            logger.info("hold_sweeper: expired %d hold(s)", swept)
    finally:
        db.close()


def run() -> None:
    settings = get_settings()
    run_as_leader("hold_sweeper", _tick, settings.hold_sweep_interval_sec)


if __name__ == "__main__":
    run()
