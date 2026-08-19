"""
[모듈] api/app/core/security.py
[담당] 공통
[역할] JWT 생성·검증, bcrypt 해싱. 도메인 로직 없는 순수 함수만.

[구현할 것]
- hash_password(raw_password) -> str
- verify_password(raw_password, password_hash) -> bool
- create_access_token(subject_id, role) -> str
- create_refresh_token(subject_id, role) -> str
- decode_token(token) -> dict | None

[의존]
- app.core.config (JWT_SECRET, 만료 시간)

[호출자]
- app.domains.auth.service (A 담당)
- app.domains.admin.service (A 담당)
- app.deps.auth (A 담당)

[주의]
- 회원 조회, refresh 토큰 저장 등 도메인 지식을 갖지 않는다. 순수 암호화/토큰
  함수만 유지해야 auth 도메인과 책임이 겹치지 않음.
- payload의 `role`("member"/"admin")은 member.id와 admin.id가 서로 다른 테이블의
  독립적인 PK라 값이 겹칠 수 있기 때문에 반드시 필요하다. role 없이 sub(id)만
  보고 조회하면 member 토큰으로 admin API가 뚫리는 권한 상승 버그가 된다.
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


def _create_token(subject_id: int, expires_delta: timedelta, token_type: str, role: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject_id),
        "type": token_type,
        "role": role,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_access_token(subject_id: int, role: str) -> str:
    settings = get_settings()
    return _create_token(
        subject_id, timedelta(minutes=settings.jwt_access_expire_min), "access", role
    )


def create_refresh_token(subject_id: int, role: str) -> str:
    settings = get_settings()
    return _create_token(
        subject_id, timedelta(days=settings.jwt_refresh_expire_days), "refresh", role
    )


def decode_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
