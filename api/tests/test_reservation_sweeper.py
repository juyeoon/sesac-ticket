"""
[모듈] api/tests/test_reservation_sweeper.py
[담당] A
[역할] 입금기한 만료 예매 정리 워커(reservation_sweeper) 테스트.
       프론트Q-백엔드-답변.md #3에서 발견된 미구현 갭을 메우는 기능.

[구현할 것]
- test_sweep_expires_overdue_pending_reservation
- test_sweep_ignores_reservations_not_yet_due
- test_sweep_ignores_already_confirmed_reservations
- test_sweep_ignores_already_expired_reservations
- test_sweep_returns_zero_when_nothing_expired

[의존]
- tests.conftest (db_session 픽스처)
- app.domains.reservation.hold_service, service, repository
- app.workers.reservation_sweeper

[호출자]
- pytest
"""

from datetime import date, time, timedelta

import pytest

from app.core.config import get_settings
from app.domains.performance.model import Category, Performance, Schedule
from app.domains.reservation import hold_service, repository, service
from app.domains.reservation.model import ScheduleSeat
from app.domains.venue.model import Venue, VenueSeat
from app.workers.reservation_sweeper import sweep_expired_reservations


@pytest.fixture(autouse=True)
def _bypass_queue_gate(monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)


def _create_schedule_with_seats(db_session, *, title: str, seat_count: int = 1) -> tuple[int, list[int]]:
    category = Category(name=f"cat-{title}", sort_order=0)
    venue = Venue(name=f"venue-{title}")
    db_session.add_all([category, venue])
    db_session.flush()

    performance = Performance(
        title=title, category_id=category.id, venue_id=venue.id, status="ACTIVE"
    )
    db_session.add(performance)
    db_session.flush()

    schedule = Schedule(
        performance_id=performance.id,
        perf_date=date.today(),
        perf_time=time(19, 0),
        status="OPEN",
    )
    db_session.add(schedule)
    db_session.flush()

    seat_ids = []
    for i in range(seat_count):
        venue_seat = VenueSeat(
            venue_id=venue.id, section="A", row_no="1", seat_no=i + 1, grade="VIP"
        )
        db_session.add(venue_seat)
        db_session.flush()

        schedule_seat = ScheduleSeat(
            schedule_id=schedule.id,
            venue_seat_id=venue_seat.id,
            grade="VIP",
            price=100000,
            status="AVAILABLE",
        )
        db_session.add(schedule_seat)
        db_session.flush()
        seat_ids.append(schedule_seat.id)

    db_session.commit()
    return schedule.id, seat_ids


def _create_reservation(db_session, *, title: str, member_id: int):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title=title)
    hold_result = hold_service.create_hold(
        db_session, member_id=member_id, schedule_id=schedule_id, seat_ids=seat_ids, entry_ticket=None
    )
    created = service.create_reservation(
        db_session, member_id=member_id, hold_id=hold_result.hold_id, depositor_name="홍길동"
    )
    return schedule_id, seat_ids, created


def _force_overdue(db_session, reservation_id: int) -> None:
    payment = repository.get_bank_transfer_payment(db_session, reservation_id)
    payment.payment_due_at = payment.payment_due_at - timedelta(days=2)
    db_session.commit()


def test_sweep_expires_overdue_pending_reservation(db_session):
    schedule_id, seat_ids, created = _create_reservation(
        db_session, title="sweep-overdue", member_id=90401
    )
    _force_overdue(db_session, created.reservation_id)

    swept = sweep_expired_reservations(db_session)

    assert swept == 1
    reservation = repository.get_reservation_by_id(db_session, created.reservation_id)
    assert reservation.status == "EXPIRED"
    assert reservation.cancelled_at is not None

    statuses = service.get_seat_status_list(db_session, schedule_id)
    assert all(item.status == "AVAILABLE" for item in statuses if item.seat_id in seat_ids)


def test_sweep_ignores_reservations_not_yet_due(db_session):
    _, _, created = _create_reservation(db_session, title="sweep-not-due", member_id=90402)

    swept = sweep_expired_reservations(db_session)

    assert swept == 0
    reservation = repository.get_reservation_by_id(db_session, created.reservation_id)
    assert reservation.status == "PENDING_PAYMENT"


def test_sweep_ignores_already_confirmed_reservations(db_session):
    _, _, created = _create_reservation(db_session, title="sweep-confirmed", member_id=90403)
    service.confirm_reservation(db_session, reservation_id=created.reservation_id, admin_id=99)
    _force_overdue(db_session, created.reservation_id)

    swept = sweep_expired_reservations(db_session)

    assert swept == 0
    reservation = repository.get_reservation_by_id(db_session, created.reservation_id)
    assert reservation.status == "CONFIRMED"


def test_sweep_ignores_already_expired_reservations(db_session):
    _, _, created = _create_reservation(db_session, title="sweep-double", member_id=90404)
    _force_overdue(db_session, created.reservation_id)
    first_pass = sweep_expired_reservations(db_session)
    assert first_pass == 1

    second_pass = sweep_expired_reservations(db_session)

    assert second_pass == 0


def test_sweep_returns_zero_when_nothing_expired(db_session):
    swept = sweep_expired_reservations(db_session)
    assert swept == 0
