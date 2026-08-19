"""
[모듈] api/app/deps/auth.py
[담당] A
[역할] Authorization 헤더의 access 토큰을 검증해 현재 로그인한 회원/관리자를 조회.

[구현할 것]
- get_current_member(credentials, db) -> Member
- get_current_admin(credentials, db) -> Admin

[의존]
- app.core.security (decode_token)
- app.domains.member.repository, app.domains.admin.repository
- app.db.routing (get_db)

[호출자]
- app.domains.reservation.router (B 담당) — 회원 인증이 필요한 전 엔드포인트

[주의]
- access 토큰만 허용한다 (payload["type"] == "access"). refresh 토큰으로는 인증 불가.
- payload["role"]이 "member"/"admin"인지도 반드시 같이 확인한다. member.id와
  admin.id는 서로 다른 테이블의 독립적인 PK라 값이 겹칠 수 있어서, role 확인
  없이 sub(id)만 보고 조회하면 member 토큰으로 admin API를 통과하는 권한
  상승 버그가 된다.
- 탈퇴(status=WITHDRAWN)한 회원은 access 토큰이 아직 만료 전이어도 접근을 거부한다.
"""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ErrorCode
from app.core.security import decode_token
from app.db.routing import get_db
from app.domains.admin import repository as admin_repository
from app.domains.admin.model import Admin
from app.domains.member import repository as member_repository
from app.domains.member.model import Member

_bearer_scheme = HTTPBearer(auto_error=False)


def _decode_access_token(
    credentials: HTTPAuthorizationCredentials | None, expected_role: str
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    payload = decode_token(credentials.credentials)
    if (
        payload is None
        or payload.get("type") != "access"
        or payload.get("role") != expected_role
    ):
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)
    return payload


def get_current_member(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> Member:
    payload = _decode_access_token(credentials, expected_role="member")
    member = member_repository.get_member_by_id(db, int(payload["sub"]))
    if member is None:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)
    if member.status == "WITHDRAWN":
        raise AppException(ErrorCode.AUTH_MEMBER_WITHDRAWN)
    return member


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    payload = _decode_access_token(credentials, expected_role="admin")
    admin = admin_repository.get_admin_by_id(db, int(payload["sub"]))
    if admin is None:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)
    return admin
