"""
[모듈] api/tests/test_reservation_seat_status.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 좌석 상태 조회(RESV-002) + Valkey 캐시 무효화 테스트.

[구현할 것]
- test_get_seat_status_list_returns_all_seats
- test_get_seat_status_populates_cache_on_first_call
- test_get_seat_status_for_missing_schedule_returns_404
- test_hold_invalidates_cache_so_status_reflects_held
- test_release_invalidates_cache_so_status_reflects_available

[의존]
- tests.conftest (db_session 픽스처)
- app.domains.reservation.service, hold_service

[호출자]
- pytest
"""

from datetime import date, time

import pytest

from app.cache.client import get_master_client
from app.cache.keys import seat_status as seat_status_key
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


def test_get_seat_status_list_returns_all_seats(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="status-basic")

    items = service.get_seat_status_list(db_session, schedule_id)

    assert len(items) == 2
    assert {item.seat_id for item in items} == set(seat_ids)
    assert all(item.section == "A" for item in items)
    assert all(item.status == "AVAILABLE" for item in items)


def test_get_seat_status_populates_cache_on_first_call(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="status-cache")

    client = get_master_client()
    assert client.hgetall(seat_status_key(schedule_id)) == {}

    service.get_seat_status_list(db_session, schedule_id)

    cached = client.hgetall(seat_status_key(schedule_id))
    assert len(cached) == 2
    assert all(v == "AVAILABLE" for v in cached.values())


def test_get_seat_status_for_missing_schedule_returns_404(db_session):
    with pytest.raises(AppException) as exc_info:
        service.get_seat_status_list(db_session, 999999)
    assert exc_info.value.error_code == ErrorCode.PERF_SCHEDULE_NOT_FOUND


def test_hold_invalidates_cache_so_status_reflects_held(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="status-hold")

    # 캐시를 먼저 채워둔다 (AVAILABLE 상태로).
    service.get_seat_status_list(db_session, schedule_id)

    hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )

    items = service.get_seat_status_list(db_session, schedule_id)
    held = next(item for item in items if item.seat_id == seat_ids[0])
    still_available = next(item for item in items if item.seat_id == seat_ids[1])

    assert held.status == "HELD"
    assert still_available.status == "AVAILABLE"


def test_release_invalidates_cache_so_status_reflects_available(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="status-release")

    result = hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )
    # Hold 직후 캐시를 한 번 채워서(HELD 상태로) 무효화가 실제로 동작하는지 검증한다.
    items = service.get_seat_status_list(db_session, schedule_id)
    assert next(i for i in items if i.seat_id == seat_ids[0]).status == "HELD"

    hold_service.release_hold(db_session, hold_id=result.hold_id, member_id=1)

    items_after = service.get_seat_status_list(db_session, schedule_id)
    assert next(i for i in items_after if i.seat_id == seat_ids[0]).status == "AVAILABLE"
