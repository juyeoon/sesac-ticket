"""
[모듈] api/app/domains/auth/router.py
[담당] A
[역할] 회원가입/로그인/토큰재발급/로그아웃 + 비밀번호 재설정 + 이메일 본인 인증.
       api 설계서 AUTH-001, 003~007, 013~014에 대응.

[구현할 것]
- POST /auth/signup -> SignUpResponse ({ userId })
- POST /auth/login -> AccessTokenResponse (refreshToken은 HttpOnly 쿠키로 발급)
- POST /auth/refresh -> AccessTokenResponse (refreshToken 쿠키로 검증)
- POST /auth/logout -> LoggedOutResponse (access 토큰 인증 필요, 쿠키 삭제)
- POST /auth/password/reset-request -> SentResponse
- POST /auth/password/reset -> ResetResponse
- POST /auth/email/verify-request -> SentResponse
- POST /auth/email/verify -> VerifiedResponse

[의존]
- app.domains.auth.service
- app.domains.auth.schema
- app.deps.auth (get_current_member, logout 인증용)
- app.db.routing (get_db)
- app.core.config (쿠키 옵션)

[호출자]
- app.api.v1

[주의]
- refreshToken은 응답 바디에 절대 넣지 않는다. HttpOnly + Secure + SameSite
  쿠키로만 주고받는다 (로컬 http 개발 시 settings.cookie_secure=False로 완화).
- 쿠키 path를 /api/v1/auth로 한정해 다른 API에는 refreshToken이 실리지 않게 한다.
"""

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.routing import get_db
from app.deps.auth import get_current_member
from app.domains.auth import service as auth_service
from app.domains.auth.schema import (
    AccessTokenResponse,
    EmailVerifyConfirmIn,
    EmailVerifyRequestIn,
    LoggedOutResponse,
    LoginRequest,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    ResetResponse,
    SentResponse,
    SignUpRequest,
    SignUpResponse,
    VerifiedResponse,
)
from app.domains.member.model import Member

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE_NAME = "refreshToken"
_REFRESH_COOKIE_PATH = "/api/v1/auth"


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.jwt_refresh_expire_days * 24 * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path=_REFRESH_COOKIE_PATH,
    )


@router.post("/signup", response_model=SignUpResponse, status_code=201)
def signup(request: SignUpRequest, db: Session = Depends(get_db)) -> SignUpResponse:
    member = auth_service.sign_up(
        db,
        email=request.email,
        password=request.password,
        nickname=request.nickname,
        gender=request.gender,
        age_range=request.age_range,
    )
    return SignUpResponse(user_id=member.id)


@router.post("/login", response_model=AccessTokenResponse)
def login(
    request: LoginRequest, response: Response, db: Session = Depends(get_db)
) -> AccessTokenResponse:
    access_token, refresh_token, expires_in = auth_service.login(
        db, email=request.email, password=request.password
    )
    _set_refresh_cookie(response, refresh_token)
    return AccessTokenResponse(access_token=access_token, expires_in=expires_in)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(
    refresh_token: str | None = Cookie(default=None, alias=_REFRESH_COOKIE_NAME),
) -> AccessTokenResponse:
    access_token, expires_in = auth_service.reissue_access_token(refresh_token)
    return AccessTokenResponse(access_token=access_token, expires_in=expires_in)


@router.post("/logout", response_model=LoggedOutResponse)
def logout(
    response: Response, member: Member = Depends(get_current_member)
) -> LoggedOutResponse:
    auth_service.logout(member.id)
    response.delete_cookie(key=_REFRESH_COOKIE_NAME, path=_REFRESH_COOKIE_PATH)
    return LoggedOutResponse()


@router.post("/password/reset-request", response_model=SentResponse)
def request_password_reset(
    request: PasswordResetRequestIn, db: Session = Depends(get_db)
) -> SentResponse:
    auth_service.request_password_reset(db, email=request.email)
    return SentResponse()


@router.post("/password/reset", response_model=ResetResponse)
def confirm_password_reset(
    request: PasswordResetConfirmIn, db: Session = Depends(get_db)
) -> ResetResponse:
    auth_service.confirm_password_reset(
        db, reset_token=request.reset_token, new_password=request.new_password
    )
    return ResetResponse()


@router.post("/email/verify-request", response_model=SentResponse)
def request_email_verification(
    request: EmailVerifyRequestIn, db: Session = Depends(get_db)
) -> SentResponse:
    auth_service.request_email_verification(db, email=request.email)
    return SentResponse()


@router.post("/email/verify", response_model=VerifiedResponse)
def confirm_email_verification(
    request: EmailVerifyConfirmIn, db: Session = Depends(get_db)
) -> VerifiedResponse:
    auth_service.confirm_email_verification(db, email=request.email, code=request.code)
    return VerifiedResponse()
