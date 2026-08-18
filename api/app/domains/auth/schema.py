"""
[모듈] api/app/domains/auth/schema.py
[담당] A
[역할] 가입·로그인 요청, 토큰 응답 DTO.

[구현할 것]
- SignUpRequest, LoginRequest, RefreshRequest
- TokenResponse, AccessTokenResponse

[의존]
- pydantic

[호출자]
- app.domains.auth.router
"""

from pydantic import BaseModel, EmailStr, Field


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    nickname: str
    gender: str | None = None
    age_range: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
