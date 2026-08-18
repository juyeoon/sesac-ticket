"""
[모듈] api/app/domains/admin/schema.py
[담당] A
[역할] 관리자 로그인 요청/응답 DTO.

[구현할 것]
- AdminLoginRequest, AdminTokenResponse

[의존]
- pydantic

[호출자]
- app.domains.admin.router
"""

from pydantic import BaseModel


class AdminLoginRequest(BaseModel):
    admin_id: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
