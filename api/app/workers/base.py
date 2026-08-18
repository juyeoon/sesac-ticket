"""
[모듈] api/app/workers/base.py
[담당] B (임시로 A가 최소 구현 — B 합류 시 리뷰 필요)
[역할] Valkey 분산 락(SET NX EX) 기반 리더 선출. api 인스턴스 2대 중 한쪽만 실제 작업 수행.

[구현할 것]
- class LeaderElection: try_acquire, renew, release
- run_as_leader(name, loop_fn, interval_sec) -> None
    리더일 때만 loop_fn을 주기 실행. SIGTERM/SIGINT 시 락 해제 후 종료.

[의존]
- app.cache.client (master 전용)
- app.cache.keys (worker_lock)

[호출자]
- app.workers.queue_dispatcher (A)
- app.workers.hold_sweeper (B, 예정)

[주의]
- 락 TTL 30초. 보유 중에는 매 루프 갱신, 보유하지 못한 인스턴스는 대기만 한다.
- 원래 이 파일은 B 담당(Day3 오전에 완성해 A에게 전달하는 것이 원칙)이나, B 작업
  착수 전이라 대기열 dispatcher 진행을 위해 A가 임시로 최소 구현했다. B가 hold_sweeper를
  만들 때 이 구현을 검토/교체할 수 있다.
"""

import logging
import signal
import time
import uuid
from typing import Callable

from app.cache.client import get_master_client
from app.cache.keys import worker_lock

logger = logging.getLogger(__name__)

_LOCK_TTL_SEC = 30


class LeaderElection:
    def __init__(self, name: str):
        self._key = worker_lock(name)
        self._token = uuid.uuid4().hex
        self._client = get_master_client()
        self._holding = False

    def try_acquire(self) -> bool:
        if self._holding:
            return self._renew()
        acquired = bool(self._client.set(self._key, self._token, nx=True, ex=_LOCK_TTL_SEC))
        self._holding = acquired
        return acquired

    def _renew(self) -> bool:
        current = self._client.get(self._key)
        if current == self._token:
            self._client.expire(self._key, _LOCK_TTL_SEC)
            return True
        self._holding = False
        return False

    def release(self) -> None:
        current = self._client.get(self._key)
        if current == self._token:
            self._client.delete(self._key)
        self._holding = False


def run_as_leader(name: str, loop_fn: Callable[[], None], interval_sec: int) -> None:
    election = LeaderElection(name)
    running = True

    def _handle_shutdown(signum, frame) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    try:
        while running:
            if election.try_acquire():
                try:
                    loop_fn()
                except Exception:
                    logger.exception("worker loop_fn failed: %s", name)
            time.sleep(interval_sec)
    finally:
        election.release()
