"""
[모듈] api/tests/test_reservation_my_list.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 내 예매 목록 조회(RESV-007) 테스트.

[구현할 것]
- test_list_my_reservations_returns_own_reservations_only
- test_list_my_reservations_filters_by_status
- test_list_my_reservations_empty_for_no_reservations

[의존]
- tests.conftest (db_session 픽스처)
- app.domains.reservation.hold_service, service

[호출자]
- pytest
"""

from datetime import date, time

import pytest

from app.core.config import get_settings
from app.domains.performance.model import Category, Performance, Schedule
from app.domains.reservation import hold_service, service
from app.domains.reservation.model import ScheduleSeat
from app.domains.venue.model import Venue, VenueSeat


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
    return service.create_reservation(
        db_session, member_id=member_id, hold_id=hold_result.hold_id, depositor_name="홍길동"
    )


def test_list_my_reservations_returns_own_reservations_only(db_session):
    # 다른 테스트 파일들도 같은(파일 기반) DB를 공유하고 롤백 없이 커밋하므로,
    # member_id는 이 테스트만의 전용 값을 써서 다른 테스트의 예매와 섞이지 않게 한다.
    _create_reservation(db_session, title="my-list-mine", member_id=90001)
    _create_reservation(db_session, title="my-list-other", member_id=90002)

    result = service.list_my_reservations(db_session, member_id=90001)

    assert result.total_elements == 1
    assert result.content[0].performance_title == "my-list-mine"


def test_list_my_reservations_filters_by_status(db_session):
    member_id = 90201
    pending = _create_reservation(db_session, title="my-list-pending", member_id=member_id)
    confirmed = _create_reservation(db_session, title="my-list-confirmed", member_id=member_id)
    service.confirm_reservation(db_session, reservation_id=confirmed.reservation_id, admin_id=99)

    pending_only = service.list_my_reservations(
        db_session, member_id=member_id, status="PENDING_PAYMENT"
    )
    confirmed_only = service.list_my_reservations(
        db_session, member_id=member_id, status="CONFIRMED"
    )

    assert pending_only.total_elements == 1
    assert pending_only.content[0].reservation_id == pending.reservation_id
    assert confirmed_only.total_elements == 1
    assert confirmed_only.content[0].reservation_id == confirmed.reservation_id


def test_list_my_reservations_empty_for_no_reservations(db_session):
    result = service.list_my_reservations(db_session, member_id=90301)

    assert result.total_elements == 0
    assert result.content == []
