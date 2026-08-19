"""
[모듈] api/app/domains/admin/service.py
[담당] A
[역할] 관리자 인증 로직 (로그인 + 토큰 재발급).

[구현할 것]
- admin_login(db, *, admin_id, password) -> tuple[access_token, refresh_token, expires_in]
- reissue_admin_access_token(refresh_token) -> tuple[access_token, expires_in]

[의존]
- app.core.security (verify_password, create_access_token, create_refresh_token, decode_token)
- app.core.config (get_settings)
- app.domains.admin.repository
- app.core.exceptions (AppException, ErrorCode)

[호출자]
- app.domains.admin.router

[주의]
- 무통장 입금 확인 처리는 이번 범위에서 제외(여유 시 추가).
- 관리자 refresh 토큰은 회원과 완전히 분리된 키(`admin:refresh:{adminId}`)에 저장한다.
"""

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.domains.admin import repository as admin_repository
from app.domains.admin.model import Admin


def admin_login(db: Session, *, admin_id: str, password: str) -> tuple[str, str, int]:
    admin = admin_repository.get_admin_by_admin_id(db, admin_id)
    if admin is None or not verify_password(password, admin.password_hash):
        raise AppException(ErrorCode.AUTH_INVALID_CREDENTIALS)

    settings = get_settings()
    access_token = create_access_token(admin.id, role="admin")
    refresh_token = create_refresh_token(admin.id, role="admin")
    admin_repository.save_admin_refresh_token(
        admin.id, refresh_token, settings.jwt_refresh_expire_days * 24 * 3600
    )
    expires_in = settings.jwt_access_expire_min * 60
    return access_token, refresh_token, expires_in


def reissue_admin_access_token(refresh_token: str | None) -> tuple[str, int]:
    if refresh_token is None:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh" or payload.get("role") != "admin":
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    admin_id = int(payload["sub"])
    stored_token = admin_repository.get_admin_refresh_token(admin_id)
    if stored_token != refresh_token:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    settings = get_settings()
    access_token = create_access_token(admin_id, role="admin")
    return access_token, settings.jwt_access_expire_min * 60
