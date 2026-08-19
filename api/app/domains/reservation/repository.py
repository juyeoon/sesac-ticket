"""
[모듈] api/app/domains/reservation/repository.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] schedule_seat / seat_hold_log에 대한 DB 접근 (Hold 관련, RESV-003/012/013 지원).

[구현할 것]
- get_seats_for_hold(db, *, schedule_id, seat_ids) -> list[ScheduleSeat]
    지정한 회차의 좌석들을 조회 (선점 가능 여부 판단용).
- mark_seats_held(db, seat_ids) -> None
- mark_seats_available(db, seat_ids) -> None
- create_seat_hold_log(db, *, hold_id, member_id, schedule_id, seat_ids, expires_at) -> SeatHoldLog
- get_seat_hold_log(db, hold_id) -> SeatHoldLog | None
- mark_hold_released(db, hold_log) -> None

[의존]
- app.domains.reservation.model (ScheduleSeat, SeatHoldLog)

[호출자]
- app.domains.reservation.hold_service

[주의]
- 이 리포지토리의 모든 함수는 writer 세션(get_db)으로만 호출한다 (분담표 원칙).
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.reservation.model import ScheduleSeat, SeatHoldLog


def get_seats_for_hold(
    db: Session, *, schedule_id: int, seat_ids: list[int]
) -> list[ScheduleSeat]:
    stmt = select(ScheduleSeat).where(
        ScheduleSeat.schedule_id == schedule_id,
        ScheduleSeat.id.in_(seat_ids),
    )
    return list(db.execute(stmt).scalars().all())


def mark_seats_held(db: Session, seat_ids: list[int]) -> None:
    seats = db.execute(
        select(ScheduleSeat).where(ScheduleSeat.id.in_(seat_ids))
    ).scalars().all()
    for seat in seats:
        seat.status = "HELD"
    db.commit()


def mark_seats_available(db: Session, seat_ids: list[int]) -> None:
    seats = db.execute(
        select(ScheduleSeat).where(ScheduleSeat.id.in_(seat_ids))
    ).scalars().all()
    for seat in seats:
        seat.status = "AVAILABLE"
    db.commit()


def create_seat_hold_log(
    db: Session,
    *,
    hold_id: str,
    member_id: int,
    schedule_id: int,
    seat_ids: list[int],
    expires_at: datetime,
) -> SeatHoldLog:
    hold_log = SeatHoldLog(
        hold_id=hold_id,
        member_id=member_id,
        schedule_id=schedule_id,
        schedule_seat_ids=seat_ids,
        status="HOLDING",
        expires_at=expires_at,
    )
    db.add(hold_log)
    db.commit()
    db.refresh(hold_log)
    return hold_log


def get_seat_hold_log(db: Session, hold_id: str) -> SeatHoldLog | None:
    stmt = select(SeatHoldLog).where(SeatHoldLog.hold_id == hold_id)
    return db.execute(stmt).scalar_one_or_none()


def mark_hold_released(db: Session, hold_log: SeatHoldLog) -> None:
    hold_log.status = "RELEASED"
    hold_log.released_at = datetime.now()
    db.commit()
