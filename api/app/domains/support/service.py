"""
[모듈] api/app/domains/support/service.py
[담당] A
[역할] 고객센터 게시글 목록/상세 조회 (API-ETC-001, 002).

[구현할 것]
- list_support_posts(db, *, page, size, category=None) -> SupportPostListResponse
- get_support_post_detail(db, post_id) -> SupportPostDetailResponse

[의존]
- app.domains.support.repository
- app.core.exceptions (SUPPORT_POST_NOT_FOUND)

[호출자]
- app.domains.support.router
"""

from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ErrorCode
from app.domains.support import repository
from app.domains.support.schema import SupportPostDetailResponse, SupportPostListResponse


def list_support_posts(
    db: Session, *, page: int, size: int, category: str | None = None
) -> SupportPostListResponse:
    items, total = repository.list_posts(db, page=page, size=size, category=category)
    return SupportPostListResponse(content=items, total_elements=total)


def get_support_post_detail(db: Session, post_id: int) -> SupportPostDetailResponse:
    post = repository.get_post_by_id(db, post_id)
    if post is None:
        raise AppException(ErrorCode.SUPPORT_POST_NOT_FOUND)
    return SupportPostDetailResponse.model_validate(post)
