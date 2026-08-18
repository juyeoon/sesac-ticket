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
        )
    return _replica_client


def eval_with_fallback(
    client: redis.Redis, sha: str, script: str, keys: list, args: list
) -> Any:
    try:
        return client.evalsha(sha, len(keys), *keys, *args)
    except redis.exceptions.NoScriptError:
        return client.eval(script, len(keys), *keys, *args)
