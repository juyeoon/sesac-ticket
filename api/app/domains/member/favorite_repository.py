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
- sqlalchemy (Core text())

[호출자]
- app.domains.member.service

[주의]
- performance/performance_image/member_favorite 테이블은 api/scripts/sql/sesac_ticket_init.sql
  기준으로 이미 존재하지만, performance/performance_image의 SQLAlchemy ORM 모델은
  아직 없다(B 담당, 미착수). 이 파일은 그 두 테이블을 SQLAlchemy ORM 모델로
  등록하지 않고 raw SQL(Core text())로만 읽는다 — B가 나중에 domains/performance
  모델을 Base.metadata에 등록할 때 테이블명이 겹쳐 충돌하는 걸 피하기 위함.
  B의 모델이 생기면 이 파일을 ORM 기반으로 교체할 수 있다.
- 테스트(SQLite)에서는 이 세 테이블이 Base.metadata에 없어 create_all()로
  안 만들어지므로, tests/conftest.py에서 별도 raw DDL로 생성한다.
"""

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session


def performance_exists(db: Session, performance_id: int) -> bool:
    row = db.execute(
        text("SELECT 1 FROM performance WHERE id = :performance_id"),
        {"performance_id": performance_id},
    ).first()
    return row is not None


def is_favorited(db: Session, member_id: int, performance_id: int) -> bool:
    row = db.execute(
        text(
            "SELECT 1 FROM member_favorite "
            "WHERE member_id = :member_id AND performance_id = :performance_id"
        ),
        {"member_id": member_id, "performance_id": performance_id},
    ).first()
    return row is not None


def add_favorite(db: Session, member_id: int, performance_id: int) -> None:
    db.execute(
        text(
            "INSERT INTO member_favorite (member_id, performance_id, created_at) "
            "VALUES (:member_id, :performance_id, :created_at)"
        ),
        {
            "member_id": member_id,
            "performance_id": performance_id,
            "created_at": datetime.now(),
        },
    )
    db.commit()


def remove_favorite(db: Session, member_id: int, performance_id: int) -> bool:
    result = db.execute(
        text(
            "DELETE FROM member_favorite "
            "WHERE member_id = :member_id AND performance_id = :performance_id"
        ),
        {"member_id": member_id, "performance_id": performance_id},
    )
    db.commit()
    return result.rowcount > 0


def list_favorites(
    db: Session, member_id: int, *, page: int, size: int
) -> tuple[list[dict], int]:
    total = db.execute(
        text("SELECT COUNT(*) FROM member_favorite WHERE member_id = :member_id"),
        {"member_id": member_id},
    ).scalar_one()

    rows = db.execute(
        text(
            "SELECT mf.performance_id AS performance_id, p.title AS title, "
            "(SELECT pi.file_key FROM performance_image pi "
            " WHERE pi.performance_id = mf.performance_id "
            " ORDER BY pi.sort_order LIMIT 1) AS thumbnail_url "
            "FROM member_favorite mf "
            "JOIN performance p ON p.id = mf.performance_id "
            "WHERE mf.member_id = :member_id "
            "ORDER BY mf.created_at DESC "
            "LIMIT :limit OFFSET :offset"
        ),
        {"member_id": member_id, "limit": size, "offset": page * size},
    ).mappings().all()

    return [dict(row) for row in rows], total
