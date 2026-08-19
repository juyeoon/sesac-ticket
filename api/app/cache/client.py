"""
[모듈] api/app/cache/client.py
[담당] 공통
[역할] Valkey master / replica 클라이언트 제공 및 EVALSHA 실패 시 EVAL 폴백 처리.

[구현할 것]
- get_master_client() -> Redis
- get_replica_client() -> Redis
- eval_with_fallback(client, sha, script, keys, args) -> Any

[의존]
- app.core.config (VALKEY_MASTER_HOST/PORT, VALKEY_REPLICA_HOST/PORT)

[호출자]
- app.cache.keys 사용자 전체 (A: refresh_token/entry_ticket/queue, B: seat_status/hold)
- app.core.lifespan (SCRIPT LOAD)

[주의]
- ZADD, ZPOPMIN, EVALSHA 등 쓰기 계열 커맨드는 master에서만 허용된다.
  replica는 read_only라 거부됨.
- protocol=2(RESP2)를 명시한다. redis-py(8.x)는 기본적으로 연결 시 HELLO로
  핸드셰이크를 시도하는데, HELLO는 Redis 6.0부터 생긴 명령이라 그보다 오래된
  서버(예: 로컬 Windows용 Redis 3.0.504)에서는 `unknown command 'HELLO'`로
  기동 자체가 실패한다. protocol=2를 명시하면 이 핸드셰이크를 건너뛰고 기존
  RESP2로 통신하므로, 신형 Valkey/Redis에서도 동일하게 잘 동작하면서 구버전
  서버와의 호환성도 확보된다.
"""

from typing import Any

import redis

from app.core.config import get_settings

_master_client: redis.Redis | None = None
_replica_client: redis.Redis | None = None


def get_master_client() -> redis.Redis:
    global _master_client
    if _master_client is None:
        settings = get_settings()
        _master_client = redis.Redis(
            host=settings.valkey_master_host,
            port=settings.valkey_master_port,
            decode_responses=True,
            protocol=2,
        )
    return _master_client


def get_replica_client() -> redis.Redis:
    global _replica_client
    if _replica_client is None:
        settings = get_settings()
        _replica_client = redis.Redis(
            host=settings.valkey_replica_host,
            port=settings.valkey_replica_port,
            decode_responses=True,
            protocol=2,
        )
    return _replica_client


def eval_with_fallback(
    client: redis.Redis, sha: str, script: str, keys: list, args: list
) -> Any:
    try:
        return client.evalsha(sha, len(keys), *keys, *args)
    except redis.exceptions.NoScriptError:
        return client.eval(script, len(keys), *keys, *args)
