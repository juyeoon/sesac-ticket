"""
[모듈] api/app/domains/queue/service.py
[담당] A
[역할] Sorted Set 진입/순번 조회. READY 전환은 workers.queue_dispatcher가 수행.
       테이블 없음 — model.py, repository.py를 만들지 않는다.

[구현할 것]
- enter(schedule_id, member_id) -> dict (status/position/estimated_wait_sec/entry_ticket)
- get_status(schedule_id, member_id) -> dict

[의존]
- app.cache.client (master 전용)
- app.cache.keys (queue, queue_ready)
- app.core.config (QUEUE_POLL_INTERVAL_SEC)
- app.core.exceptions

[호출자]
- app.domains.queue.router

[주의]
- (1) 전부 Valkey master. replica는 ZADD/ZPOPMIN 거부됨.
- (2) 롱폴링 금지. ALB idle timeout 60초에 잘림. 클라이언트가 settings.QUEUE_POLL_INTERVAL_SEC
      간격(기본 3초)으로 폴링.
- (3) 상태는 WAITING → READY → ENTERED → EXPIRED. 이 서비스는 WAITING/READY만 다루며
      ENTERED/EXPIRED 전이는 예매(B) 쪽에서 entryTicket 소비/만료로 결정된다.
- 예상 대기시간은 순번 × 폴링 주기의 고정 계수 근사치이며 실제 처리 속도를 반영하지 않는다.
"""

import time

from app.cache.client import get_master_client
from app.cache.keys import queue as queue_key
from app.cache.keys import queue_ready as queue_ready_key
from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode


def enter(schedule_id: int, member_id: int) -> dict:
    client = get_master_client()
    client.zadd(queue_key(schedule_id), {str(member_id): time.time()}, nx=True)
    return _status(schedule_id, member_id)


def get_status(schedule_id: int, member_id: int) -> dict:
    return _status(schedule_id, member_id)


def _status(schedule_id: int, member_id: int) -> dict:
    client = get_master_client()

    ready_ticket = client.get(queue_ready_key(schedule_id, member_id))
    if ready_ticket is not None:
        return {
            "schedule_id": schedule_id,
            "status": "READY",
            "position": 0,
            "estimated_wait_sec": 0,
            "entry_ticket": ready_ticket,
        }

    rank = client.zrank(queue_key(schedule_id), str(member_id))
    if rank is None:
        raise AppException(ErrorCode.QUEUE_NOT_ENTERED)

    position = rank + 1
    settings = get_settings()
    return {
        "schedule_id": schedule_id,
        "status": "WAITING",
        "position": position,
        "estimated_wait_sec": position * settings.queue_poll_interval_sec,
        "entry_ticket": None,
    }
