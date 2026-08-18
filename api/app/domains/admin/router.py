"""
[모듈] api/app/domains/admin/router.py
[담당] A
[역할] 관리자 로그인 + 토큰 재발급. api 설계서 ADMIN-007/008에 대응.

[구현할 것]
- POST /admin/auth/login -> AdminAccessTokenResponse (+ adminRefreshToken 쿠키 발급)
- POST /admin/auth/refresh -> AdminAccessTokenResponse (adminRefreshToken 쿠키로 검증)

[의존]
- app.domains.admin.service
- app.domains.admin.schema
- app.db.routing (get_db)
- app.core.config (쿠키 옵션)

[호출자]
- app.api.v1

[주의]
- adminRefreshToken은 응답 바디에 넣지 않는다 — HttpOnly + Secure + SameSite 쿠키로만
  전달하며, 쿠키명을 `refreshToken`(회원용)과 다르게 `adminRefreshToken`으로 분리해
  일반 회원 토큰과 완전히 구분한다.
"""

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.routing import get_db
from app.domains.admin import service as admin_service
from app.domains.admin.schema import AdminAccessTokenResponse, AdminLoginRequest

router = APIRouter(prefix="/admin/auth", tags=["admin"])

_ADMIN_REFRESH_COOKIE_NAME = "adminRefreshToken"
_ADMIN_REFRESH_COOKIE_PATH = "/api/v1/admin/auth"


def _set_admin_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=_ADMIN_REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.jwt_refresh_expire_days * 24 * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path=_ADMIN_REFRESH_COOKIE_PATH,
    )


@router.post("/login", response_model=AdminAccessTokenResponse)
def login(
    request: AdminLoginRequest, response: Response, db: Session = Depends(get_db)
) -> AdminAccessTokenResponse:
    access_token, refresh_token, expires_in = admin_service.admin_login(
        db, admin_id=request.admin_id, password=request.password
    )
    _set_admin_refresh_cookie(response, refresh_token)
    return AdminAccessTokenResponse(access_token=access_token, expires_in=expires_in)


@router.post("/refresh", response_model=AdminAccessTokenResponse)
def refresh(
    refresh_token: str | None = Cookie(default=None, alias=_ADMIN_REFRESH_COOKIE_NAME),
) -> AdminAccessTokenResponse:
    access_token, expires_in = admin_service.reissue_admin_access_token(refresh_token)
    return AdminAccessTokenResponse(access_token=access_token, expires_in=expires_in)
