"""
[모듈] api/app/domains/member/favorite_repository.py
[담당] A
[역할] 관심 공연(member_favorite) 조회/등록/삭제.

[구현할 것]
- performance_exists(db, performance_id) -> bool
- is_favorited(db, member_id, performance_id) -> bool
- add_favorite(db, member_id, performance_id) -> None
- remove_favorite(db, member_id, performance_id) -> bool (삭제된 행이 있으면 True)
- list_favorites(db, member_id, *, page, size) -> tuple[list[dict], int]
    dict 형태: {performance_id, title, thumbnail_url}

[의존]
- app.domains.member.model (MemberFavorite)
- app.domains.performance.model (Performance, PerformanceImage) — B 담당

[호출자]
- app.domains.member.service

[주의]
- B의 domains/performance 모델이 없던 시점엔 raw SQL(Core text())로 구현했었으나,
  B의 ORM 모델이 merge된 뒤로 정식 ORM 기반으로 교체함.
- 썸네일은 Performance.images 관계(에서 sort_order로 정렬됨)의 첫 번째 항목을 쓴다.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.member.model import MemberFavorite
from app.domains.performance.model import Performance


def performance_exists(db: Session, performance_id: int) -> bool:
    return db.get(Performance, performance_id) is not None


def is_favorited(db: Session, member_id: int, performance_id: int) -> bool:
    stmt = select(MemberFavorite.id).where(
        MemberFavorite.member_id == member_id,
        MemberFavorite.performance_id == performance_id,
    )
    return db.execute(stmt).first() is not None


def add_favorite(db: Session, member_id: int, performance_id: int) -> None:
    db.add(MemberFavorite(member_id=member_id, performance_id=performance_id))
    db.commit()


def remove_favorite(db: Session, member_id: int, performance_id: int) -> bool:
    stmt = select(MemberFavorite).where(
        MemberFavorite.member_id == member_id,
        MemberFavorite.performance_id == performance_id,
    )
    favorite = db.execute(stmt).scalar_one_or_none()
    if favorite is None:
        return False

    db.delete(favorite)
    db.commit()
    return True


def list_favorites(
    db: Session, member_id: int, *, page: int, size: int
) -> tuple[list[dict], int]:
    total = db.execute(
        select(func.count())
        .select_from(MemberFavorite)
        .where(MemberFavorite.member_id == member_id)
    ).scalar_one()

    stmt = (
        select(MemberFavorite, Performance)
        .join(Performance, Performance.id == MemberFavorite.performance_id)
        .where(MemberFavorite.member_id == member_id)
        .order_by(MemberFavorite.created_at.desc())
        .limit(size)
        .offset(page * size)
    )

    items = []
    for _favorite, performance in db.execute(stmt).all():
        thumbnail_url = performance.images[0].file_key if performance.images else None
        items.append(
            {
                "performance_id": performance.id,
                "title": performance.title,
                "thumbnail_url": thumbnail_url,
            }
        )

    return items, total
