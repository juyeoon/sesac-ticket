"""
[모듈] api/app/domains/member/schema.py
[담당] A
[역할] 회원 응답 DTO.

[구현할 것]
- class MemberResponse(BaseModel)

[의존]
- pydantic

[호출자]
- app.domains.auth.router (회원가입 응답)
- app.deps.auth

[주의]
- password_hash 절대 미포함.
"""

from pydantic import BaseModel, ConfigDict


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nickname: str
    gender: str | None
    age_range: str | None
    status: str
    email_verified: bool
