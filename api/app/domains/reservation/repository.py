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
- mark_hold_converted(db, hold_log) -> None
- mark_seats_pending_payment(db, seat_ids) -> None
    예매 생성 시점(RESV-004) — HELD -> PENDING_PAYMENT. 관리자 확정 전까지는
    이 상태로 남아 프론트가 "입금대기중"으로 구분해서 보여줄 수 있게 한다.
- mark_seats_reserved(db, seat_ids) -> None
    관리자 확정 시점(RESV-005) — PENDING_PAYMENT -> RESERVED. 여기서 비로소
    "예매 완료" 확정.
- create_reservation_with_payment(db, *, ...) -> Reservation
    reservation/reservation_seat/bank_transfer_payment를 한 트랜잭션으로 INSERT (RESV-004).
- get_reservation_by_id(db, reservation_id) -> Reservation | None
- get_bank_transfer_payment(db, reservation_id) -> BankTransferPayment | None
- get_expired_pending_reservations(db, *, now) -> list[Reservation]
    reservation_sweeper가 사용 — status=PENDING_PAYMENT이면서 payment_due_at이 지난 것들.
- get_reservation_seat_ids(db, reservation_id) -> list[int]
- mark_reservation_expired(db, reservation) -> None
- get_schedule_with_performance(db, schedule_id) -> Schedule | None
- get_reservation_seats_detail(db, reservation_id) -> list[dict]
- list_reservations_by_member(db, member_id, *, status=None) -> tuple[list[dict], int]
    RESV-007 — 반드시 writer 세션으로 호출 (복제 지연으로 방금 만든 예매가 안 보이는 문제 방지).
    페이지네이션 없음 (프론트가 목록형 API에서 페이지네이션을 쓰지 않기로 함 —
    member/favorite_repository.list_favorites와 동일한 결정).
- mark_hold_expired(db, hold_log) -> None
- get_expired_holding_holds(db, *, now) -> list[SeatHoldLog]
    hold_sweeper가 사용 — status=HOLDING이면서 expires_at이 지난 것들.
- list_all_reservations_admin(db) -> list[dict]
    관리자 대시보드용 전체 예매 목록 (GET /reservations/list). 페이지네이션 없음 —
    회원용 목록(list_reservations_by_member)과 마찬가지로 전체 반환. N+1로 좌석을
    조회하지만(get_reservation_seats_detail 재사용) 관리자용 저빈도 조회라 문제 없음.

[의존]
- app.domains.reservation.model (ScheduleSeat, SeatHoldLog, Reservation, ReservationSeat)
- app.domains.payment.model (BankTransferPayment)
- app.domains.venue.model (VenueSeat) — JOIN용
- app.domains.performance.model (Schedule, Performance) — 존재 확인/JOIN용

[호출자]
- app.domains.reservation.hold_service, app.domains.reservation.service

[주의]
- 이 리포지토리의 모든 함수는 writer 세션(get_db)으로만 호출한다 (분담표 원칙).
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domains.member.model import Member
from app.domains.payment.model import BankTransferPayment
from app.domains.performance.model import Performance, Schedule
from app.domains.reservation.model import (
    Reservation,
    ReservationSeat,
    ScheduleSeat,
    SeatHoldLog,
)
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
    hold_log.released_at = datetime.now(timezone.utc)
    db.commit()


def mark_hold_converted(db: Session, hold_log: SeatHoldLog) -> None:
    hold_log.status = "CONVERTED"
    db.commit()


def mark_hold_expired(db: Session, hold_log: SeatHoldLog) -> None:
    hold_log.status = "EXPIRED"
    hold_log.released_at = datetime.now(timezone.utc)
    db.commit()


def get_expired_holding_holds(db: Session, *, now: datetime) -> list[SeatHoldLog]:
    stmt = select(SeatHoldLog).where(
        SeatHoldLog.status == "HOLDING",
        SeatHoldLog.expires_at < now,
    )
    return list(db.execute(stmt).scalars().all())


def mark_seats_pending_payment(db: Session, seat_ids: list[int]) -> None:
    seats = db.execute(
        select(ScheduleSeat).where(ScheduleSeat.id.in_(seat_ids))
    ).scalars().all()
    for seat in seats:
        seat.status = "PENDING_PAYMENT"
    db.commit()


def mark_seats_reserved(db: Session, seat_ids: list[int]) -> None:
    seats = db.execute(
        select(ScheduleSeat).where(ScheduleSeat.id.in_(seat_ids))
    ).scalars().all()
    for seat in seats:
        seat.status = "RESERVED"
    db.commit()


def create_reservation_with_payment(
    db: Session,
    *,
    member_id: int,
    schedule_id: int,
    hold_id: str,
    seats: list[ScheduleSeat],
    depositor_name: str,
    bank_account_info: str,
    payment_due_at: datetime,
) -> Reservation:
    total_amount = sum(seat.price for seat in seats)
    reservation = Reservation(
        member_id=member_id,
        schedule_id=schedule_id,
        hold_id=hold_id,
        payment_method="BANK_TRANSFER",
        status="PENDING_PAYMENT",
        total_amount=total_amount,
    )
    db.add(reservation)
    db.flush()

    for seat in seats:
        db.add(
            ReservationSeat(
                reservation_id=reservation.id,
                schedule_seat_id=seat.id,
                price_snapshot=seat.price,
            )
        )

    db.add(
        BankTransferPayment(
            reservation_id=reservation.id,
            depositor_name=depositor_name,
            bank_account_info=bank_account_info,
            payment_due_at=payment_due_at,
        )
    )

    db.commit()
    db.refresh(reservation)
    return reservation


def get_reservation_by_id(db: Session, reservation_id: int) -> Reservation | None:
    return db.get(Reservation, reservation_id)


def get_bank_transfer_payment(db: Session, reservation_id: int) -> BankTransferPayment | None:
    stmt = select(BankTransferPayment).where(
        BankTransferPayment.reservation_id == reservation_id
    )
    return db.execute(stmt).scalar_one_or_none()


def get_expired_pending_reservations(db: Session, *, now: datetime) -> list[Reservation]:
    stmt = (
        select(Reservation)
        .join(BankTransferPayment, BankTransferPayment.reservation_id == Reservation.id)
        .where(
            Reservation.status == "PENDING_PAYMENT",
            BankTransferPayment.payment_due_at < now,
        )
    )
    return list(db.execute(stmt).scalars().all())


def get_reservation_seat_ids(db: Session, reservation_id: int) -> list[int]:
    stmt = select(ReservationSeat.schedule_seat_id).where(
        ReservationSeat.reservation_id == reservation_id
    )
    return [row[0] for row in db.execute(stmt).all()]


def mark_reservation_expired(db: Session, reservation: Reservation) -> None:
    reservation.status = "EXPIRED"
    reservation.cancelled_at = datetime.now(timezone.utc)
    db.commit()


def get_schedule_with_performance(db: Session, schedule_id: int) -> Schedule | None:
    stmt = (
        select(Schedule)
        .join(Performance, Performance.id == Schedule.performance_id)
        .where(Schedule.id == schedule_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def get_reservation_seats_detail(db: Session, reservation_id: int) -> list[dict]:
    stmt = (
        select(
            VenueSeat.section,
            VenueSeat.row_no,
            VenueSeat.seat_no,
            ScheduleSeat.grade,
            ReservationSeat.price_snapshot,
        )
        .select_from(ReservationSeat)
        .join(ScheduleSeat, ScheduleSeat.id == ReservationSeat.schedule_seat_id)
        .join(VenueSeat, VenueSeat.id == ScheduleSeat.venue_seat_id)
        .where(ReservationSeat.reservation_id == reservation_id)
        .order_by(VenueSeat.section, VenueSeat.row_no, VenueSeat.seat_no)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "section": row.section,
            "row": row.row_no,
            "number": row.seat_no,
            "grade": row.grade,
            "price": row.price_snapshot,
        }
        for row in rows
    ]


def list_reservations_by_member(
    db: Session, member_id: int, *, status: str | None = None
) -> tuple[list[dict], int]:
    filters = [Reservation.member_id == member_id]
    if status is not None:
        filters.append(Reservation.status == status)

    stmt = (
        select(Reservation, Performance.title, Schedule.perf_date)
        .join(Schedule, Schedule.id == Reservation.schedule_id)
        .join(Performance, Performance.id == Schedule.performance_id)
        .where(*filters)
        .order_by(Reservation.created_at.desc())
    )

    items = [
        {
            "reservation_id": reservation.id,
            "performance_title": title,
            "date": perf_date,
            "status": reservation.status,
            "confirmed_at": reservation.confirmed_at,
        }
        for reservation, title, perf_date in db.execute(stmt).all()
    ]

    return items, len(items)


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


def list_all_reservations_admin(db: Session) -> list[dict]:
    stmt = (
        select(
            Reservation,
            Member.id,
            Member.nickname,
            Member.email,
            Performance.id,
            Performance.title,
            Schedule.id,
            Schedule.perf_date,
            Schedule.perf_time,
            BankTransferPayment.depositor_name,
        )
        .join(Member, Member.id == Reservation.member_id)
        .join(Schedule, Schedule.id == Reservation.schedule_id)
        .join(Performance, Performance.id == Schedule.performance_id)
        .outerjoin(BankTransferPayment, BankTransferPayment.reservation_id == Reservation.id)
        .order_by(Reservation.created_at.desc())
    )
    rows = db.execute(stmt).all()

    items = []
    for (
        reservation,
        member_id,
        nickname,
        email,
        performance_id,
        performance_title,
        schedule_id,
        perf_date,
        perf_time,
        depositor_name,
    ) in rows:
        items.append(
            {
                "reservation_id": reservation.id,
                "status": reservation.status,
                "confirmed_at": reservation.confirmed_at,
                "depositor_name": depositor_name,
                "member": {"member_id": member_id, "nickname": nickname, "email": email},
                "performance": {"performance_id": performance_id, "title": performance_title},
                "schedule": {"schedule_id": schedule_id, "date": perf_date, "time": perf_time},
                "seats": get_reservation_seats_detail(db, reservation.id),
            }
        )
    return items
