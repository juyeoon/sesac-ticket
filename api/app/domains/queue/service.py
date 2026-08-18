"""
[모듈] api/app/domains/queue/service.py
[담당] A
[역할] Sorted Set 진입/순번 조회 (api 설계서 TRF-001/002 규격). READY 전환은
       workers.queue_dispatcher가 수행. 테이블 없음 — model.py, repository.py를 만들지 않는다.

[구현할 것]
- enter(performance_id, schedule_id, member_id) -> dict (queue_token/position/estimated_wait_seconds)
- get_status(queue_token) -> dict (status/position/estimated_wait_seconds/entry_ticket)

[의존]
- app.cache.client (master 전용)
- app.cache.keys (queue, queue_token, queue_ready)
- app.core.config (QUEUE_POLL_INTERVAL_SEC, QUEUE_TOKEN_TTL_SEC)
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
- get_status는 api 설계서상 인증이 불필요하다 — queueToken 자체가 자격증명이다.
  member_id는 진입(enter) 시점에만 필요하고, 이후 조회는 토큰만으로 이루어진다.
- queue:token:{token} 값은 "memberId:performanceId:scheduleId" 형식의 문자열이다.
  스케줄별 Sorted Set(queue:{performanceId}:{scheduleId})에서 순번을 다시 계산하려면
  performanceId/scheduleId를 알아야 하므로 함께 저장한다.
"""

import time
import uuid

from app.cache.client import get_master_client
from app.cache.keys import queue as queue_key
from app.cache.keys import queue_ready as queue_ready_key
from app.cache.keys import queue_token as queue_token_key
from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode


def enter(performance_id: int, schedule_id: int, member_id: int) -> dict:
    client = get_master_client()
    settings = get_settings()

    token = uuid.uuid4().hex
    client.zadd(queue_key(performance_id, schedule_id), {token: time.time()})
    client.set(
        queue_token_key(token),
        f"{member_id}:{performance_id}:{schedule_id}",
        ex=settings.queue_token_ttl_sec,
    )

    rank = client.zrank(queue_key(performance_id, schedule_id), token)
    position = (rank or 0) + 1
    return {
        "queue_token": token,
        "position": position,
        "estimated_wait_seconds": position * settings.queue_poll_interval_sec,
    }


def get_status(queue_token: str) -> dict:
    client = get_master_client()

    mapping = client.get(queue_token_key(queue_token))
    if mapping is None:
        raise AppException(ErrorCode.QUEUE_NOT_ENTERED)

    ready_ticket = client.get(queue_ready_key(queue_token))
    if ready_ticket is not None:
        return {
            "status": "READY",
            "position": 0,
            "estimated_wait_seconds": 0,
            "entry_ticket": ready_ticket,
        }

    _member_id, performance_id, schedule_id = mapping.split(":", 2)
    rank = client.zrank(queue_key(int(performance_id), int(schedule_id)), queue_token)
    if rank is None:
        raise AppException(ErrorCode.QUEUE_NOT_ENTERED)

    settings = get_settings()
    position = rank + 1
    return {
        "status": "WAITING",
        "position": position,
        "estimated_wait_seconds": position * settings.queue_poll_interval_sec,
        "entry_ticket": None,
    }
