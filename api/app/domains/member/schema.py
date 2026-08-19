"""
[모듈] api/app/domains/member/schema.py
[담당] A
[역할] 회원/관심공연 응답 DTO. api 설계서(AUTH-008~012)의 camelCase 규격을 따른다.

[구현할 것]
- MemberResponse
- MemberUpdateRequest (nickname/gender/ageRange 선택 + verificationCode 필수)
- MemberWithdrawRequest (password, 본인 확인용 — 설계서엔 없는 보안 강화)
- UpdateResponse ({ updated })
- WithdrawResponse ({ deleted })
- FavoriteItem / FavoriteListResponse ({ content, totalElements })
- FavoritedResponse ({ favorited })

[의존]
- pydantic

[호출자]
- app.domains.auth.router (회원가입 응답에서는 SignUpResponse를 쓰고 MemberResponse는 미사용)
- app.domains.member.router

[주의]
- password_hash 절대 미포함.
- preferredGenres는 member 테이블에 컬럼이 없어 이번 정합화에서 제외했다
  (스키마 변경 필요 + B와 공유 중인 init.sql을 건드리게 되어 보류).
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class MemberResponse(_CamelModel):
    id: int
    email: str
    nickname: str
    gender: str | None
    age_range: str | None
    status: str
    email_verified: bool


class MemberUpdateRequest(_CamelModel):
    nickname: str | None = None
    gender: str | None = None
    age_range: str | None = None
    verification_code: str


class MemberWithdrawRequest(_CamelModel):
    password: str


class UpdateResponse(_CamelModel):
    updated: bool = True


class WithdrawResponse(_CamelModel):
    deleted: bool = True


class FavoriteItem(_CamelModel):
    performance_id: int
    title: str
    thumbnail_url: str | None = None


class FavoriteListResponse(_CamelModel):
    content: list[FavoriteItem]
    total_elements: int


class FavoritedResponse(_CamelModel):
    favorited: bool
