"""
[모듈] api/app/domains/support/schema.py
[담당] A
[역할] 고객센터 게시글 응답 DTO. api 설계서 규격(camelCase)을 따른다.

[구현할 것]
- SupportPostItem ({ id, title, category, createdAt }) — API-ETC-001 목록 항목
- SupportPostListResponse ({ content, totalElements }) — API-ETC-001 응답
- SupportPostDetailResponse ({ id, title, content, category, createdAt }) — API-ETC-002 응답

[의존]
- pydantic

[호출자]
- app.domains.support.service, router
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class SupportPostItem(_CamelModel):
    id: int
    title: str
    category: str | None
    created_at: datetime


class SupportPostListResponse(_CamelModel):
    content: list[SupportPostItem]
    total_elements: int


class SupportPostDetailResponse(_CamelModel):
    id: int
    title: str
    content: str
    category: str | None
    created_at: datetime
