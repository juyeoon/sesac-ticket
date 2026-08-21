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
    # status(ACTIVE/HIDDEN/ENDED)로 걸러버리면 예매 종료된 공연은 상세 조회 자체가
    # 404가 되어 정보도 못 보여준다. 상세는 status 무관하게 항상 내려주고,
    # "예매 가능 여부"는 응답의 status 필드를 보고 프론트가 버튼을 비활성화한다.
    stmt = (
        select(Performance)
        .where(Performance.id == performance_id)
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


def get_schedule_by_id(db, schedule_id):
    stmt = (
        select(Schedule)
        .where(Schedule.id == schedule_id)
        .options(joinedload(Schedule.performance).joinedload(Performance.venue))
    )
    return db.scalars(stmt).unique().one_or_none()
