"""
[모듈] api/app/deps/auth.py
[담당] A
[역할] Authorization 헤더의 access 토큰을 검증해 현재 로그인한 회원/관리자를 조회.

[구현할 것]
- get_current_member(authorization, db) -> Member
- get_current_admin(authorization, db) -> Admin

[의존]
- app.core.security (decode_token)
- app.domains.member.repository, app.domains.admin.repository
- app.db.routing (get_db)

[호출자]
- app.domains.reservation.router (B 담당) — 회원 인증이 필요한 전 엔드포인트

[주의]
- access 토큰만 허용한다 (payload["type"] == "access"). refresh 토큰으로는 인증 불가.
"""

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ErrorCode
from app.core.security import decode_token
from app.db.routing import get_db
from app.domains.admin import repository as admin_repository
from app.domains.admin.model import Admin
from app.domains.member import repository as member_repository
from app.domains.member.model import Member


def _decode_access_token(authorization: str | None) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)
    return payload


def get_current_member(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Member:
    payload = _decode_access_token(authorization)
    member = member_repository.get_member_by_id(db, int(payload["sub"]))
    if member is None:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)
    return member


def get_current_admin(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Admin:
    payload = _decode_access_token(authorization)
    admin = admin_repository.get_admin_by_id(db, int(payload["sub"]))
    if admin is None:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)
    return admin
