"""
[모듈] api/tests/test_hold_sweeper.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] Hold 만료 워커(hold_sweeper) 테스트.

[구현할 것]
- test_sweep_expired_holds_returns_seat_to_available
- test_sweep_ignores_holds_not_yet_expired
- test_sweep_ignores_already_released_holds
- test_sweep_returns_zero_when_nothing_expired

[의존]
- tests.conftest (db_session 픽스처)
- app.workers.hold_sweeper
- app.domains.reservation.hold_service

[호출자]
- pytest
"""

from datetime import date, time

import pytest

from app.core.config import get_settings
from app.domains.performance.model import Category, Performance, Schedule
from app.domains.reservation import hold_service, repository, service
from app.domains.reservation.model import ScheduleSeat
from app.domains.venue.model import Venue, VenueSeat
from app.workers.hold_sweeper import sweep_expired_holds


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


def _force_expire(db_session, hold_id: str) -> None:
    from datetime import timedelta

    hold_log = repository.get_seat_hold_log(db_session, hold_id)
    hold_log.expires_at = hold_log.expires_at - timedelta(days=1)
    db_session.commit()


def test_sweep_expired_holds_returns_seat_to_available(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="sweep-basic")
    result = hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=seat_ids, entry_ticket=None
    )
    _force_expire(db_session, result.hold_id)

    swept = sweep_expired_holds(db_session)

    assert swept == 1
    hold_log = repository.get_seat_hold_log(db_session, result.hold_id)
    assert hold_log.status == "EXPIRED"
    seats = service.get_seat_status_list(db_session, schedule_id)
    assert all(item.status == "AVAILABLE" for item in seats)


def test_sweep_ignores_holds_not_yet_expired(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="sweep-not-expired")
    hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=seat_ids, entry_ticket=None
    )

    swept = sweep_expired_holds(db_session)

    assert swept == 0
    seats = service.get_seat_status_list(db_session, schedule_id)
    assert all(item.status == "HELD" for item in seats)


def test_sweep_ignores_already_released_holds(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="sweep-released")
    result = hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=seat_ids, entry_ticket=None
    )
    hold_service.release_hold(db_session, hold_id=result.hold_id, member_id=1)
    _force_expire(db_session, result.hold_id)

    swept = sweep_expired_holds(db_session)

    assert swept == 0
    hold_log = repository.get_seat_hold_log(db_session, result.hold_id)
    assert hold_log.status == "RELEASED"


def test_sweep_returns_zero_when_nothing_expired(db_session):
    swept = sweep_expired_holds(db_session)
    assert swept == 0
