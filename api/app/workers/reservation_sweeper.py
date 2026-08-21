"""
[모듈] api/app/workers/reservation_sweeper.py
[담당] A
[역할] 입금기한(payment_due_at)이 지났는데 관리자가 확정/취소하지 않은 무통장입금
       예매를 주기적으로 찾아 EXPIRED 처리하고 좌석을 AVAILABLE로 되돌린다.
       (프론트Q-백엔드-답변.md #3 — hold_sweeper가 다루지 못하는, "Hold 이후
       예매까지 생성됐지만 입금이 안 들어온" 케이스를 처리)

[구현할 것]
- sweep_expired_reservations(db) -> int (되돌린 예매 개수)
- run() -> None (리더일 때만 무한 루프)

[의존]
- app.workers.base (리더 선출, hold_sweeper/queue_dispatcher와 동일)
- app.domains.reservation.repository (get_expired_pending_reservations)
- app.domains.reservation.service (expire_reservation — 좌석 복구 + 캐시 무효화)
- app.db.session (WriterSessionLocal — FastAPI 요청 밖이라 get_db Depends를 못 씀)

[호출자]
- systemd (sesac-reservation-sweeper.service, hold_sweeper/queue_dispatcher와 동일한 배포 방식)

[주의]
- hold_sweeper는 "좌석 선점(Hold) 후 예매 생성 전"에 시간 초과된 것만 처리한다.
  이 워커는 그 다음 단계 — "예매는 생성됐지만(PENDING_PAYMENT) 입금기한이 지나도록
  관리자가 확정도 취소도 안 한" 것을 처리한다. 두 워커는 서로 겹치는 대상이 없다
  (hold_log.status가 CONVERTED로 바뀌는 순간부터는 hold_sweeper 대상에서 빠짐).
- 각 tick마다 새 writer 세션을 열고 닫는다 — 장시간 유지되는 세션을 피하기 위함.
- 리더 선출 키가 "reservation_sweeper"로 hold_sweeper("hold_sweeper")와 다르므로
  두 워커는 서로 독립적으로 리더를 선출한다 (한쪽이 죽어도 다른 쪽은 영향 없음).
"""

import logging
from datetime import datetime, timezone

from app.core.config import get_settings
from app.db.session import WriterSessionLocal
from app.domains.reservation import repository
from app.domains.reservation.service import expire_reservation
from app.workers.base import run_as_leader

logger = logging.getLogger(__name__)


def sweep_expired_reservations(db) -> int:
    expired = repository.get_expired_pending_reservations(db, now=datetime.now(timezone.utc))
    for reservation in expired:
        expire_reservation(db, reservation)
    return len(expired)


def _tick() -> None:
    db = WriterSessionLocal()
    try:
        swept = sweep_expired_reservations(db)
        if swept:
            logger.info("reservation_sweeper: expired %d reservation(s)", swept)
    finally:
        db.close()


def run() -> None:
    settings = get_settings()
    run_as_leader("reservation_sweeper", _tick, settings.reservation_sweep_interval_sec)


if __name__ == "__main__":
    run()
