"""
[모듈] api/app/domains/auth/service.py
[담당] A
[역할] 회원가입 중복 검사, 로그인 검증, 토큰 발급/재발급/폐기.

[구현할 것]
- sign_up(db, *, email, password, nickname, gender, age_range) -> Member
- login(db, *, email, password) -> tuple[access_token, refresh_token]
- reissue_access_token(refresh_token) -> access_token
- logout(refresh_token) -> None

[의존]
- app.core.security (hash_password, verify_password, create_access_token,
  create_refresh_token, decode_token)
- app.domains.member.repository
- app.domains.auth.repository
- app.core.exceptions (AppException, ErrorCode)

[호출자]
- app.domains.auth.router

[주의]
- refresh 재발급 시 Valkey에 저장된 토큰과 요청 토큰이 일치하는지 반드시 대조한다
  (로그아웃되었거나 재사용된 refresh 토큰 차단).
"""

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ErrorCode
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.domains.auth import repository as auth_repository
from app.domains.member import repository as member_repository
from app.domains.member.model import Member


def sign_up(
    db: Session,
    *,
    email: str,
    password: str,
    nickname: str,
    gender: str | None,
    age_range: str | None,
) -> Member:
    if member_repository.get_member_by_email(db, email) is not None:
        raise AppException(ErrorCode.AUTH_EMAIL_ALREADY_EXISTS)

    password_hash = hash_password(password)
    return member_repository.create_member(
        db,
        email=email,
        password_hash=password_hash,
        nickname=nickname,
        gender=gender,
        age_range=age_range,
    )


def login(db: Session, *, email: str, password: str) -> tuple[str, str]:
    member = member_repository.get_member_by_email(db, email)
    if member is None or not verify_password(password, member.password_hash):
        raise AppException(ErrorCode.AUTH_INVALID_CREDENTIALS)

    access_token = create_access_token(member.id)
    refresh_token = create_refresh_token(member.id)
    auth_repository.save_refresh_token(member.id, refresh_token)
    return access_token, refresh_token


def reissue_access_token(refresh_token: str) -> str:
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    member_id = int(payload["sub"])
    stored_token = auth_repository.get_refresh_token(member_id)
    if stored_token != refresh_token:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    return create_access_token(member_id)


def logout(refresh_token: str) -> None:
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    auth_repository.delete_refresh_token(int(payload["sub"]))
