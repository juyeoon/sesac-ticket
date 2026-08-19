"""
[모듈] api/app/workers/queue_dispatcher.py
[담당] A
[역할] 주기적으로 대기열 앞쪽 N개 queueToken을 ZPOPMIN → entryTicket 발급 → READY 전환.

[구현할 것]
- dispatch_once(performance_id, schedule_id) -> int (발급된 인원 수)
- run() -> None (리더일 때만 무한 루프)

[의존]
- app.cache.client, app.cache.keys
- app.core.config (QUEUE_DISPATCH_BATCH_SIZE, QUEUE_POLL_INTERVAL_SEC)
- app.workers.base (리더 선출)
- app.db.session (ReaderSessionLocal) — 활성 회차 목록 조회용
- app.domains.performance.model (Schedule)
- app.domains.venue.model — 직접 쓰진 않지만, Performance.venue가 문자열 참조라
  이 모듈이 import돼서 Venue 클래스가 매퍼 registry에 등록돼 있어야 함

[호출자]
- systemd (sesac-dispatcher.service)

[주의]
- workers.base는 B 담당 모듈. Day3 오전에 B가 완성해서 넘겨주는 게 원칙이나, B 작업
  착수 전이라 A가 임시 구현한 버전을 그대로 사용 중이다. 리더 선출 코드를 여기서
  다시 구현하지 말 것.
- 활성 회차(schedule) 목록은 Schedule.status == "OPEN"인 것 전체를 매 틱마다
  reader로 조회한다. 복제 지연으로 방금 CLOSED된 회차가 한두 틱 더 잡혀도
  dispatch_once가 좌석 재고를 바꾸는 건 아니라서 무해하다.
- API 앱 프로세스는 venue 라우터 등록 경로로 domains.venue.model이 이미 import돼
  있어서 이 문제가 안 드러나지만, 이 워커는 완전히 별도 프로세스라 독립적으로
  import해줘야 한다 (tests/conftest.py가 같은 이유로 동일하게 처리해둔 패턴).
- ZPOPMIN으로 꺼낸 각 queueToken의 실제 member_id는 queue:token:{token} 매핑에서
  읽는다. 매핑이 이미 만료(TTL 종료)됐다면 해당 항목은 건너뛴다.
"""

import logging
import uuid

from sqlalchemy import select

from app.cache.client import get_master_client
from app.cache.keys import entry_ticket as entry_ticket_key
from app.cache.keys import queue as queue_key
from app.cache.keys import queue_ready as queue_ready_key
from app.cache.keys import queue_token as queue_token_key
from app.core.config import get_settings
from app.db.session import ReaderSessionLocal
from app.domains.performance.model import Schedule
from app.domains.venue import model as _venue_model  # noqa: F401
from app.workers.base import run_as_leader

logger = logging.getLogger(__name__)

_ENTRY_TICKET_TTL_SEC = 300


def dispatch_once(performance_id: int, schedule_id: int) -> int:
    settings = get_settings()
    client = get_master_client()
    popped = client.zpopmin(
        queue_key(performance_id, schedule_id), settings.queue_dispatch_batch_size
    )

    dispatched = 0
    for token, _score in popped:
        mapping = client.get(queue_token_key(token))
        if mapping is None:
            continue

        member_id = mapping.split(":", 1)[0]
        ticket_id = uuid.uuid4().hex
        client.set(entry_ticket_key(ticket_id), member_id, ex=_ENTRY_TICKET_TTL_SEC)
        client.set(queue_ready_key(token), ticket_id, ex=_ENTRY_TICKET_TTL_SEC)
        dispatched += 1

    return dispatched


def _fetch_active_schedule_ids() -> list[tuple[int, int]]:
    db = ReaderSessionLocal()
    try:
        rows = db.execute(
            select(Schedule.performance_id, Schedule.id).where(Schedule.status == "OPEN")
        ).all()
        return [(row.performance_id, row.id) for row in rows]
    finally:
        db.close()


def _dispatch_all_schedules() -> None:
    for performance_id, schedule_id in _fetch_active_schedule_ids():
        dispatched = dispatch_once(performance_id, schedule_id)
        if dispatched:
            logger.info(
                "dispatched %d entries: performance=%s schedule=%s",
                dispatched,
                performance_id,
                schedule_id,
            )


def run() -> None:
    settings = get_settings()
    run_as_leader("queue_dispatcher", _dispatch_all_schedules, settings.queue_poll_interval_sec)


if __name__ == "__main__":
    run()
