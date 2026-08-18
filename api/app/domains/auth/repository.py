"""
[모듈] api/app/domains/auth/repository.py
[담당] A
[역할] refresh 토큰 / 비밀번호 재설정 토큰 / 이메일 인증 코드의 Valkey 읽기/쓰기.

[구현할 것]
- save_refresh_token(member_id, token) -> None
- get_refresh_token(member_id) -> str | None
- delete_refresh_token(member_id) -> None
- save_password_reset_token(token, member_id, ttl_sec) -> None
- get_password_reset_member_id(token) -> int | None
- delete_password_reset_token(token) -> None
- save_email_verification_code(email, code, ttl_sec) -> None
- get_email_verification_code(email) -> str | None
- delete_email_verification_code(email) -> None
- is_email_verification_cooling_down(email) -> bool
- start_email_verification_cooldown(email, ttl_sec) -> None

[의존]
- app.cache.client (master 클라이언트만 사용)
- app.cache.keys
- app.core.config

[호출자]
- app.domains.auth.service

[주의]
- 반드시 master 전용. replica는 read_only라 SET/DEL이 거부됨.
"""

from app.cache.client import get_master_client
from app.cache.keys import email_verification_code as email_verification_code_key
from app.cache.keys import email_verification_cooldown as email_verification_cooldown_key
from app.cache.keys import password_reset_token as password_reset_token_key
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


def save_password_reset_token(token: str, member_id: int, ttl_sec: int) -> None:
    client = get_master_client()
    client.set(password_reset_token_key(token), str(member_id), ex=ttl_sec)


def get_password_reset_member_id(token: str) -> int | None:
    client = get_master_client()
    value = client.get(password_reset_token_key(token))
    return int(value) if value is not None else None


def delete_password_reset_token(token: str) -> None:
    client = get_master_client()
    client.delete(password_reset_token_key(token))


def save_email_verification_code(email: str, code: str, ttl_sec: int) -> None:
    client = get_master_client()
    client.set(email_verification_code_key(email), code, ex=ttl_sec)


def get_email_verification_code(email: str) -> str | None:
    client = get_master_client()
    return client.get(email_verification_code_key(email))


def delete_email_verification_code(email: str) -> None:
    client = get_master_client()
    client.delete(email_verification_code_key(email))


def is_email_verification_cooling_down(email: str) -> bool:
    client = get_master_client()
    return bool(client.exists(email_verification_cooldown_key(email)))


def start_email_verification_cooldown(email: str, ttl_sec: int) -> None:
    client = get_master_client()
    client.set(email_verification_cooldown_key(email), "1", ex=ttl_sec)
