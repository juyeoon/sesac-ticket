"""
[모듈] api/app/domains/reservation/repository.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] schedule_seat / seat_hold_log에 대한 DB 접근. Hold(RESV-003/012/013)와
       좌석 상태 조회(RESV-002) 양쪽에서 사용.

[구현할 것]
- get_seats_for_hold(db, *, schedule_id, seat_ids) -> list[ScheduleSeat]
    지정한 회차의 좌석들을 조회 (선점 가능 여부 판단용).
- mark_seats_held(db, seat_ids) -> None
- mark_seats_available(db, seat_ids) -> None
- create_seat_hold_log(db, *, hold_id, member_id, schedule_id, seat_ids, expires_at) -> SeatHoldLog
- get_seat_hold_log(db, hold_id) -> SeatHoldLog | None
- mark_hold_released(db, hold_log) -> None
- schedule_exists(db, schedule_id) -> bool
- get_schedule_seats_with_seat_info(db, schedule_id) -> list[dict]
    schedule_seat를 venue_seat와 JOIN해서 section/row/number까지 포함한 좌석 목록 반환.

[의존]
- app.domains.reservation.model (ScheduleSeat, SeatHoldLog)
- app.domains.venue.model (VenueSeat) — JOIN용
- app.domains.performance.model (Schedule) — 존재 확인용

[호출자]
- app.domains.reservation.hold_service, app.domains.reservation.service

[주의]
- 이 리포지토리의 모든 함수는 writer 세션(get_db)으로만 호출한다 (분담표 원칙).
"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.performance.model import Schedule
from app.domains.reservation.model import ScheduleSeat, SeatHoldLog
from app.domains.venue.model import VenueSeat


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


def schedule_exists(db: Session, schedule_id: int) -> bool:
    return db.get(Schedule, schedule_id) is not None


def get_schedule_seats_with_seat_info(db: Session, schedule_id: int) -> list[dict]:
    stmt = (
        select(
            ScheduleSeat.id,
            VenueSeat.section,
            VenueSeat.row_no,
            VenueSeat.seat_no,
            ScheduleSeat.grade,
            ScheduleSeat.status,
        )
        .join(VenueSeat, VenueSeat.id == ScheduleSeat.venue_seat_id)
        .where(ScheduleSeat.schedule_id == schedule_id)
        .order_by(VenueSeat.section, VenueSeat.row_no, VenueSeat.seat_no)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "seat_id": row.id,
            "section": row.section,
            "row": row.row_no,
            "number": row.seat_no,
            "grade": row.grade,
            "status": row.status,
        }
        for row in rows
    ]
