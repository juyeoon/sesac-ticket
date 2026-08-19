"""
[모듈] api/app/domains/support/repository.py
[담당] A
[역할] support_post 테이블 조회 전용 접근. api 설계서 API-ETC-001/002 대응.

[구현할 것]
- list_posts(db, *, page, size, category=None) -> tuple[list[SupportPost], int]
- get_post_by_id(db, post_id) -> SupportPost | None

[의존]
- app.domains.support.model (SupportPost)

[호출자]
- app.domains.support.service

[주의]
- 조회 전용 도메인이라 반드시 get_read_db 세션으로 호출한다 (writer 원칙은
  reservation처럼 쓰기 도메인에만 해당).
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.support.model import SupportPost


def list_posts(
    db: Session, *, page: int, size: int, category: str | None = None
) -> tuple[list[SupportPost], int]:
    filters = []
    if category is not None:
        filters.append(SupportPost.category == category)

    total = db.execute(
        select(func.count()).select_from(SupportPost).where(*filters)
    ).scalar_one()

    stmt = (
        select(SupportPost)
        .where(*filters)
        .order_by(SupportPost.created_at.desc())
        .limit(size)
        .offset(page * size)
    )
    items = list(db.execute(stmt).scalars().all())

    return items, total


def get_post_by_id(db: Session, post_id: int) -> SupportPost | None:
    return db.get(SupportPost, post_id)
