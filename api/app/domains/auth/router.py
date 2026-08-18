"""
[모듈] api/app/domains/auth/router.py
[담당] A
[역할] 회원가입 / 로그인 / 토큰 재발급 / 로그아웃 4개 엔드포인트.

[구현할 것]
- POST /auth/signup -> MemberResponse
- POST /auth/login -> TokenResponse
- POST /auth/refresh -> AccessTokenResponse
- POST /auth/logout -> 204

[의존]
- app.domains.auth.service
- app.domains.auth.schema
- app.domains.member.schema (MemberResponse)
- app.db.routing (get_db)

[호출자]
- app.api.v1
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.routing import get_db
from app.domains.auth import service as auth_service
from app.domains.auth.schema import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    SignUpRequest,
    TokenResponse,
)
from app.domains.member.schema import MemberResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=MemberResponse, status_code=201)
def signup(request: SignUpRequest, db: Session = Depends(get_db)) -> MemberResponse:
    member = auth_service.sign_up(
        db,
        email=request.email,
        password=request.password,
        nickname=request.nickname,
        gender=request.gender,
        age_range=request.age_range,
    )
    return MemberResponse.model_validate(member)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access_token, refresh_token = auth_service.login(
        db, email=request.email, password=request.password
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(request: RefreshRequest) -> AccessTokenResponse:
    access_token = auth_service.reissue_access_token(request.refresh_token)
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=204)
def logout(request: RefreshRequest) -> None:
    auth_service.logout(request.refresh_token)
