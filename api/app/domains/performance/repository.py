from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.domains.performance.model import Performance, Schedule


def list_performances(db):
    stmt = (
        select(Performance)
        .options(
            joinedload(Performance.category),
            joinedload(Performance.venue),
            selectinload(Performance.images),
            selectinload(Performance.schedules),
        )
        .order_by(Performance.id)
    )
    return list(db.scalars(stmt).unique().all())


def search_performances(db, keyword):
    stmt = (
        select(Performance)
        .where(Performance.title.like(f"%{keyword}%"))
        .options(
            joinedload(Performance.category),
            joinedload(Performance.venue),
            selectinload(Performance.images),
            selectinload(Performance.schedules),
        )
        .order_by(Performance.id)
    )
    return list(db.scalars(stmt).unique().all())


def get_performance_detail(db, performance_id):
    stmt = (
        select(Performance)
        .where(Performance.id == performance_id, Performance.status == "ACTIVE")
        .options(
            joinedload(Performance.category),
            joinedload(Performance.venue),
            selectinload(Performance.images),
            selectinload(Performance.seat_grades),
            selectinload(Performance.schedules),
        )
    )
    return db.scalars(stmt).unique().one_or_none()


def list_schedules(db, performance_id):
    stmt = (
        select(Schedule)
        .where(Schedule.performance_id == performance_id)
        .options(joinedload(Schedule.performance))
        .order_by(Schedule.perf_date, Schedule.perf_time)
    )
    return list(db.scalars(stmt).unique().all())
