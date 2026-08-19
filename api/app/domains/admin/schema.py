"""
[모듈] api/app/domains/admin/schema.py
[담당] A
[역할] 관리자 로그인/토큰재발급 요청·응답 DTO. api 설계서 ADMIN-007/008 규격(camelCase)을 따른다.

[구현할 것]
- AdminLoginRequest ({ adminId, password })
- AdminAccessTokenResponse ({ accessToken, tokenType, expiresIn })

[의존]
- pydantic

[호출자]
- app.domains.admin.router

[주의]
- adminRefreshToken은 응답 바디에 넣지 않는다 — HttpOnly 쿠키로만 전달한다
  (일반 회원의 refreshToken 쿠키와는 이름이 다른 별도 쿠키).
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AdminLoginRequest(_CamelModel):
    admin_id: str
    password: str


class AdminAccessTokenResponse(_CamelModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
