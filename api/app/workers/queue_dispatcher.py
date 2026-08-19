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

[호출자]
- systemd (sesac-dispatcher.service)

[주의]
- workers.base는 B 담당 모듈. Day3 오전에 B가 완성해서 넘겨주는 게 원칙이나, B 작업
  착수 전이라 A가 임시 구현한 버전을 그대로 사용 중이다. 리더 선출 코드를 여기서
  다시 구현하지 말 것.
- 활성 회차(schedule) 목록 조회는 B의 performance/schedule 도메인이 준비되어야
  가능하다. 그 전까지 _dispatch_all_schedules는 자리표시자이며, dispatch_once만
  단위로 테스트 가능하다.
- ZPOPMIN으로 꺼낸 각 queueToken의 실제 member_id는 queue:token:{token} 매핑에서
  읽는다. 매핑이 이미 만료(TTL 종료)됐다면 해당 항목은 건너뛴다.
"""

import logging
import uuid

from app.cache.client import get_master_client
from app.cache.keys import entry_ticket as entry_ticket_key
from app.cache.keys import queue as queue_key
from app.cache.keys import queue_ready as queue_ready_key
from app.cache.keys import queue_token as queue_token_key
from app.core.config import get_settings
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


def _dispatch_all_schedules() -> None:
    # TODO: B의 performance/schedule 도메인이 준비되면 활성 (performance_id, schedule_id)
    # 목록을 조회해 각각에 대해 dispatch_once를 호출하도록 교체한다.
    logger.debug("queue dispatcher tick (no active schedule source wired yet)")


def run() -> None:
    settings = get_settings()
    run_as_leader("queue_dispatcher", _dispatch_all_schedules, settings.queue_poll_interval_sec)


if __name__ == "__main__":
    run()
