"""
[모듈] api/app/domains/auth/repository.py
[담당] A
[역할] refresh 토큰의 Valkey 읽기/쓰기.

[구현할 것]
- save_refresh_token(member_id, token) -> None
- get_refresh_token(member_id) -> str | None
- delete_refresh_token(member_id) -> None

[의존]
- app.cache.client (master 클라이언트만 사용)
- app.cache.keys (refresh_token)
- app.core.config

[호출자]
- app.domains.auth.service

[주의]
- 반드시 master 전용. replica는 read_only라 SET/DEL이 거부됨.
"""

from app.cache.client import get_master_client
from app.cache.keys import refresh_token as refresh_token_key
from app.core.config import get_settings


def save_refresh_token(member_id: int, token: str) -> None:
    settings = get_settings()
    client = get_master_client()
    client.set(
        refresh_token_key(member_id),
        token,
        ex=settings.jwt_refresh_expire_days * 24 * 3600,
    )


def get_refresh_token(member_id: int) -> str | None:
    client = get_master_client()
    return client.get(refresh_token_key(member_id))


def delete_refresh_token(member_id: int) -> None:
    client = get_master_client()
    client.delete(refresh_token_key(member_id))
