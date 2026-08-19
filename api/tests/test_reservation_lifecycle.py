"""
[모듈] api/tests/test_reservation_lifecycle.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 무통장입금 예매 생성/확정/조회(RESV-004, 005, 006) 테스트.

[구현할 것]
- test_create_reservation_success
- test_create_reservation_fails_for_hold_not_found
- test_create_reservation_fails_for_wrong_owner
- test_create_reservation_fails_for_expired_hold
- test_confirm_reservation_success
- test_confirm_reservation_fails_for_already_confirmed
- test_confirm_reservation_fails_for_not_found
- test_get_reservation_detail_success
- test_get_reservation_detail_fails_for_wrong_owner
- test_get_reservation_detail_fails_for_not_found

[의존]
- tests.conftest (db_session 픽스처)
- app.domains.reservation.hold_service, service

[호출자]
- pytest
"""

from datetime import date, time

import pytest

from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.domains.performance.model import Category, Performance, Schedule
from app.domains.reservation import hold_service, service
from app.domains.reservation.model import ScheduleSeat
from app.domains.venue.model import Venue, VenueSeat


@pytest.fixture(autouse=True)
def _bypass_queue_gate(monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)


def _create_schedule_with_seats(db_session, *, title: str, seat_count: int = 2) -> tuple[int, list[int]]:
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


def _create_hold(db_session, *, title: str, member_id: int = 1):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title=title)
    result = hold_service.create_hold(
        db_session, member_id=member_id, schedule_id=schedule_id, seat_ids=seat_ids, entry_ticket=None
    )
    return schedule_id, seat_ids, result.hold_id


def test_create_reservation_success(db_session):
    schedule_id, seat_ids, hold_id = _create_hold(db_session, title="resv-create")

    result = service.create_reservation(
        db_session, member_id=1, hold_id=hold_id, depositor_name="홍길동"
    )

    assert result.status == "PENDING_PAYMENT"
    assert result.payment_method == "BANK_TRANSFER"
    assert result.bank_account_info

    statuses = service.get_seat_status_list(db_session, schedule_id)
    assert all(item.status == "RESERVED" for item in statuses if item.seat_id in seat_ids)


def test_create_reservation_fails_for_hold_not_found(db_session):
    with pytest.raises(AppException) as exc_info:
        service.create_reservation(
            db_session, member_id=1, hold_id="nonexistent", depositor_name="홍길동"
        )
    assert exc_info.value.error_code == ErrorCode.RESV_HOLD_NOT_FOUND


def test_create_reservation_fails_for_wrong_owner(db_session):
    _, _, hold_id = _create_hold(db_session, title="resv-wrong-owner", member_id=1)

    with pytest.raises(AppException) as exc_info:
        service.create_reservation(
            db_session, member_id=2, hold_id=hold_id, depositor_name="홍길동"
        )
    assert exc_info.value.error_code == ErrorCode.RESV_HOLD_OWNER_MISMATCH


def test_create_reservation_fails_for_expired_hold(db_session):
    _, _, hold_id = _create_hold(db_session, title="resv-expired", member_id=1)
    hold_service.release_hold(db_session, hold_id=hold_id, member_id=1)

    with pytest.raises(AppException) as exc_info:
        service.create_reservation(
            db_session, member_id=1, hold_id=hold_id, depositor_name="홍길동"
        )
    assert exc_info.value.error_code == ErrorCode.RESV_HOLD_EXPIRED


def test_confirm_reservation_success(db_session):
    _, _, hold_id = _create_hold(db_session, title="resv-confirm")
    created = service.create_reservation(
        db_session, member_id=1, hold_id=hold_id, depositor_name="홍길동"
    )

    result = service.confirm_reservation(
        db_session, reservation_id=created.reservation_id, admin_id=99
    )

    assert result.status == "CONFIRMED"
    assert result.confirmed_at is not None


def test_confirm_reservation_fails_for_already_confirmed(db_session):
    _, _, hold_id = _create_hold(db_session, title="resv-double-confirm")
    created = service.create_reservation(
        db_session, member_id=1, hold_id=hold_id, depositor_name="홍길동"
    )
    service.confirm_reservation(db_session, reservation_id=created.reservation_id, admin_id=99)

    with pytest.raises(AppException) as exc_info:
        service.confirm_reservation(
            db_session, reservation_id=created.reservation_id, admin_id=99
        )
    assert exc_info.value.error_code == ErrorCode.RESV_INVALID_STATUS_TRANSITION


def test_confirm_reservation_fails_for_not_found(db_session):
    with pytest.raises(AppException) as exc_info:
        service.confirm_reservation(db_session, reservation_id=999999, admin_id=99)
    assert exc_info.value.error_code == ErrorCode.RESV_NOT_FOUND


def test_get_reservation_detail_success(db_session):
    schedule_id, seat_ids, hold_id = _create_hold(db_session, title="resv-detail")
    created = service.create_reservation(
        db_session, member_id=1, hold_id=hold_id, depositor_name="홍길동"
    )

    detail = service.get_reservation_detail(
        db_session, reservation_id=created.reservation_id, member_id=1
    )

    assert detail.reservation_id == created.reservation_id
    assert detail.performance.title == "resv-detail"
    assert detail.schedule.schedule_id == schedule_id
    assert len(detail.seats) == len(seat_ids)
    assert detail.status == "PENDING_PAYMENT"
    assert detail.bank_account_info


def test_get_reservation_detail_fails_for_wrong_owner(db_session):
    _, _, hold_id = _create_hold(db_session, title="resv-detail-wrong-owner", member_id=1)
    created = service.create_reservation(
        db_session, member_id=1, hold_id=hold_id, depositor_name="홍길동"
    )

    with pytest.raises(AppException) as exc_info:
        service.get_reservation_detail(
            db_session, reservation_id=created.reservation_id, member_id=2
        )
    assert exc_info.value.error_code == ErrorCode.RESV_OWNER_MISMATCH


def test_get_reservation_detail_fails_for_not_found(db_session):
    with pytest.raises(AppException) as exc_info:
        service.get_reservation_detail(db_session, reservation_id=999999, member_id=1)
    assert exc_info.value.error_code == ErrorCode.RESV_NOT_FOUND
