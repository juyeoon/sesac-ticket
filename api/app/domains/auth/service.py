"""
[모듈] api/app/domains/auth/service.py
[담당] A
[역할] 회원가입 중복 검사, 로그인 검증, 토큰 발급/재발급/폐기,
       비밀번호 재설정, 이메일 본인 인증.

[구현할 것]
- sign_up(db, *, email, password, nickname, gender, age_range) -> Member
- login(db, *, email, password) -> tuple[access_token, refresh_token, expires_in]
- reissue_access_token(refresh_token) -> tuple[access_token, expires_in]
- logout(member_id) -> None
- request_password_reset(db, *, email) -> None
- confirm_password_reset(db, *, reset_token, new_password) -> None
- request_email_verification(db, *, email) -> None
- confirm_email_verification(db, *, email, code) -> None

[의존]
- app.core.security (hash_password, verify_password, create_access_token,
  create_refresh_token, decode_token)
- app.core.config (get_settings)
- app.core.mailer (send_mail)
- app.domains.member.repository
- app.domains.auth.repository
- app.core.exceptions (AppException, ErrorCode)

[호출자]
- app.domains.auth.router

[주의]
- refresh 재발급 시 Valkey에 저장된 토큰과 요청 토큰이 일치하는지 반드시 대조한다
  (로그아웃되었거나 재사용된 refresh 토큰 차단).
- 탈퇴(status=WITHDRAWN)한 회원은 비밀번호가 맞아도 로그인을 거부한다.
- 비밀번호 재설정 요청/이메일 인증 요청은 가입 여부와 무관하게 항상 성공으로
  응답한다 (이메일 존재 여부를 노출하는 사용자 열거 공격 방지).
- 비밀번호 재설정 성공 시 기존 refresh 세션을 강제 폐기한다 (재로그인 유도).
- logout은 이제 refresh 토큰이 아니라 access 토큰으로 인증된 member_id를 받는다
  (api 설계서 AUTH-013의 "인증: 필요"는 access 토큰 기준).
"""

import secrets

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.core.mailer import send_mail
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


def login(db: Session, *, email: str, password: str) -> tuple[str, str, int]:
    member = member_repository.get_member_by_email(db, email)
    if member is None or not verify_password(password, member.password_hash):
        raise AppException(ErrorCode.AUTH_INVALID_CREDENTIALS)

    if member.status == "WITHDRAWN":
        raise AppException(ErrorCode.AUTH_MEMBER_WITHDRAWN)

    settings = get_settings()
    access_token = create_access_token(member.id)
    refresh_token = create_refresh_token(member.id)
    auth_repository.save_refresh_token(member.id, refresh_token)
    expires_in = settings.jwt_access_expire_min * 60
    return access_token, refresh_token, expires_in


def reissue_access_token(refresh_token: str | None) -> tuple[str, int]:
    if refresh_token is None:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    member_id = int(payload["sub"])
    stored_token = auth_repository.get_refresh_token(member_id)
    if stored_token != refresh_token:
        raise AppException(ErrorCode.AUTH_TOKEN_INVALID)

    settings = get_settings()
    access_token = create_access_token(member_id)
    return access_token, settings.jwt_access_expire_min * 60


def logout(member_id: int) -> None:
    auth_repository.delete_refresh_token(member_id)


def request_password_reset(db: Session, *, email: str) -> None:
    member = member_repository.get_member_by_email(db, email)
    if member is not None:
        settings = get_settings()
        token = secrets.token_urlsafe(32)
        auth_repository.save_password_reset_token(
            token, member.id, settings.password_reset_ttl_sec
        )
        send_mail(
            email,
            "[새싹티켓] 비밀번호 재설정",
            f"아래 토큰으로 비밀번호를 재설정하세요 (유효시간 {settings.password_reset_ttl_sec // 60}분): {token}",
        )
    # 가입 여부와 무관하게 항상 성공 응답 (사용자 열거 공격 방지)


def confirm_password_reset(db: Session, *, reset_token: str, new_password: str) -> None:
    member_id = auth_repository.get_password_reset_member_id(reset_token)
    if member_id is None:
        raise AppException(ErrorCode.AUTH_PASSWORD_RESET_TOKEN_INVALID)

    member = member_repository.get_member_by_id(db, member_id)
    if member is None:
        raise AppException(ErrorCode.AUTH_PASSWORD_RESET_TOKEN_INVALID)

    member_repository.set_password_hash(db, member, hash_password(new_password))
    auth_repository.delete_password_reset_token(reset_token)
    auth_repository.delete_refresh_token(member_id)


def request_email_verification(db: Session, *, email: str) -> None:
    member = member_repository.get_member_by_email(db, email)
    if member is None:
        return  # 가입 여부와 무관하게 항상 성공 응답 (사용자 열거 공격 방지)

    if auth_repository.is_email_verification_cooling_down(email):
        raise AppException(ErrorCode.AUTH_EMAIL_VERIFICATION_TOO_MANY_REQUESTS)

    settings = get_settings()
    code = f"{secrets.randbelow(1_000_000):06d}"
    auth_repository.save_email_verification_code(
        email, code, settings.email_verification_ttl_sec
    )
    auth_repository.start_email_verification_cooldown(
        email, settings.email_verification_cooldown_sec
    )
    send_mail(email, "[새싹티켓] 이메일 인증 코드", f"인증 코드: {code}")


def confirm_email_verification(db: Session, *, email: str, code: str) -> None:
    stored_code = auth_repository.get_email_verification_code(email)
    if stored_code is None or stored_code != code:
        raise AppException(ErrorCode.AUTH_EMAIL_VERIFICATION_CODE_INVALID)

    member = member_repository.get_member_by_email(db, email)
    if member is None:
        raise AppException(ErrorCode.AUTH_EMAIL_VERIFICATION_CODE_INVALID)

    member_repository.mark_email_verified(db, member)
    auth_repository.delete_email_verification_code(email)
