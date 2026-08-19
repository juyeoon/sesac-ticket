"""
[모듈] api/app/domains/auth/schema.py
[담당] A
[역할] 인증 관련 요청/응답 DTO. api 설계서(AUTH-001~007, 013~014)의 필드명(camelCase)을 따른다.

[구현할 것]
- SignUpRequest / SignUpResponse ({ userId })
- LoginRequest / AccessTokenResponse ({ accessToken, tokenType, expiresIn })
- PasswordResetRequestIn ({ email }) / SentResponse ({ sent })
- PasswordResetConfirmIn ({ resetToken, newPassword }) / ResetResponse ({ reset })
- EmailVerifyRequestIn ({ email }) / SentResponse
- EmailVerifyConfirmIn ({ email, code }) / VerifiedResponse ({ verified })
- LoggedOutResponse ({ loggedOut })

[의존]
- pydantic

[호출자]
- app.domains.auth.router

[주의]
- 응답/요청 바디는 api 설계서 규격(camelCase)을 따른다. Python 코드 내부는
  snake_case로 다루고, alias_generator=to_camel + populate_by_name=True로
  camelCase JSON과 자동 매핑한다 (snake_case로 보내도 여전히 허용됨).
- refreshToken은 응답 바디에 넣지 않는다 — HttpOnly 쿠키로만 전달한다
  (app.domains.auth.router._set_refresh_cookie 참고).
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class SignUpRequest(_CamelModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    nickname: str
    gender: str | None = None
    age_range: str | None = None


class SignUpResponse(_CamelModel):
    user_id: int


class LoginRequest(_CamelModel):
    email: EmailStr
    password: str


class AccessTokenResponse(_CamelModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class SentResponse(_CamelModel):
    sent: bool = True


class ResetResponse(_CamelModel):
    reset: bool = True


class VerifiedResponse(_CamelModel):
    verified: bool = True


class LoggedOutResponse(_CamelModel):
    logged_out: bool = True


class PasswordResetRequestIn(_CamelModel):
    email: EmailStr


class PasswordResetConfirmIn(_CamelModel):
    reset_token: str
    new_password: str = Field(min_length=8, max_length=72)


class EmailVerifyRequestIn(_CamelModel):
    email: EmailStr


class EmailVerifyConfirmIn(_CamelModel):
    email: EmailStr
    code: str
