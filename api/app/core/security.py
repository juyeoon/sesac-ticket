"""
[모듈] api/app/core/security.py
[담당] 공통
[역할] JWT 생성·검증, bcrypt 해싱. 도메인 로직 없는 순수 함수만.

[구현할 것]
- hash_password(raw_password) -> str
- verify_password(raw_password, password_hash) -> bool
- create_access_token(member_id) -> str
- create_refresh_token(member_id) -> str
- decode_token(token) -> dict | None

[의존]
- app.core.config (JWT_SECRET, 만료 시간)

[호출자]
- app.domains.auth.service (A 담당)
- app.deps.auth (A 담당)

[주의]
- 회원 조회, refresh 토큰 저장 등 도메인 지식을 갖지 않는다. 순수 암호화/토큰
  함수만 유지해야 auth 도메인과 책임이 겹치지 않음.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings


def hash_password(raw_password: str) -> str:
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(raw_password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))


def _create_token(member_id: int, expires_delta: timedelta, token_type: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(member_id),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_access_token(member_id: int) -> str:
    settings = get_settings()
    return _create_token(member_id, timedelta(minutes=settings.jwt_access_expire_min), "access")


def create_refresh_token(member_id: int) -> str:
    settings = get_settings()
    return _create_token(
        member_id, timedelta(days=settings.jwt_refresh_expire_days), "refresh"
    )


def decode_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
