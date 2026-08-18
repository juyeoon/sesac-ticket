"""
[모듈] api/app/cache/client.py
[담당] 공통
[역할] Valkey master / replica 클라이언트 제공 및 EVALSHA 실패 시 EVAL 폴백 처리.

[구현할 것]
- get_master_client() -> Redis
    쓰기/Lua 실행 전용 클라이언트.
- get_replica_client() -> Redis
    읽기 전용 클라이언트.
- eval_with_fallback(client, sha: str, script: str, keys: list, args: list) -> Any
    EVALSHA 시도 → NOSCRIPT 에러 시 EVAL로 재시도.

[의존]
- app.core.config (VALKEY_MASTER_HOST/PORT, VALKEY_REPLICA_HOST/PORT)

[호출자]
- app.cache.keys 사용자 전체 (A: refresh_token/entry_ticket/queue, B: seat_status/hold)
- app.core.lifespan (SCRIPT LOAD)

[주의]
- ZADD, ZPOPMIN, EVALSHA 등 쓰기 계열 커맨드는 master에서만 허용된다.
  replica는 read_only라 거부됨.

[TODO] 구현 필요
"""

def get_master_client():
    pass


def get_replica_client():
    pass


def eval_with_fallback(client, sha, script, keys, args):
    pass
