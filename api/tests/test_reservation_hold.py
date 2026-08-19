"""
[모듈] api/tests/test_reservation_hold.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 좌석 임시 선점/해제/상태조회(hold_service) 테스트. RESV-003, 012, 013.

[구현할 것]
- test_create_hold_success
- test_create_hold_fails_for_missing_seat
- test_create_hold_fails_for_already_held_seat
- test_create_hold_requires_entry_ticket_when_queue_enabled
- test_two_concurrent_holds_on_same_seat_only_one_succeeds (가장 중요한 테스트)
- test_release_hold_success_returns_seat_to_available
- test_release_hold_wrong_owner_returns_403
- test_release_hold_already_released_returns_expired
- test_get_hold_success_returns_remaining_seconds
- test_get_hold_wrong_owner_returns_403
- test_get_hold_nonexistent_returns_404

[의존]
- tests.conftest (db_session 픽스처)
- app.domains.reservation.hold_service

[호출자]
- pytest
"""

from datetime import date, time

import pytest

from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.domains.performance.model import Category, Performance, Schedule
from app.domains.reservation import hold_service, repository
from app.domains.reservation.model import ScheduleSeat
from app.domains.venue.model import Venue, VenueSeat


@pytest.fixture(autouse=True)
def _bypass_queue_gate(monkeypatch):
    # 이 파일의 테스트는 Hold 로직 자체에 집중한다. entryTicket 게이트는
    # test_queue.py / test_create_hold_requires_entry_ticket_when_queue_enabled
    # 에서 별도로 검증하므로, 기본값은 꺼둔다.
    monkeypatch.setattr(get_settings(), "queue_enabled", False)


def _create_schedule_with_seats(db_session, *, title: str, seat_count: int = 3) -> tuple[int, list[int]]:
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


def test_create_hold_success(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="hold-ok")

    result = hold_service.create_hold(
        db_session,
        member_id=1,
        schedule_id=schedule_id,
        seat_ids=seat_ids[:2],
        entry_ticket=None,
    )

    assert result.seat_ids == seat_ids[:2]
    assert result.hold_id

    hold_log = repository.get_seat_hold_log(db_session, result.hold_id)
    assert hold_log.status == "HOLDING"
    assert hold_log.member_id == 1

    seats = repository.get_seats_for_hold(db_session, schedule_id=schedule_id, seat_ids=seat_ids[:2])
    assert all(s.status == "HELD" for s in seats)
    # 선점 안 한 세 번째 좌석은 그대로 AVAILABLE
    remaining_seat = repository.get_seats_for_hold(
        db_session, schedule_id=schedule_id, seat_ids=[seat_ids[2]]
    )[0]
    assert remaining_seat.status == "AVAILABLE"


def test_create_hold_fails_for_missing_seat(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="hold-missing")

    with pytest.raises(AppException) as exc_info:
        hold_service.create_hold(
            db_session,
            member_id=1,
            schedule_id=schedule_id,
            seat_ids=[*seat_ids, 999999],
            entry_ticket=None,
        )
    assert exc_info.value.error_code == ErrorCode.RESV_SEAT_NOT_FOUND


def test_create_hold_fails_for_already_held_seat(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="hold-dup")

    hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )

    with pytest.raises(AppException) as exc_info:
        hold_service.create_hold(
            db_session,
            member_id=2,
            schedule_id=schedule_id,
            seat_ids=[seat_ids[0]],
            entry_ticket=None,
        )
    assert exc_info.value.error_code == ErrorCode.RESV_SEAT_ALREADY_HELD


def test_create_hold_requires_entry_ticket_when_queue_enabled(db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", True)
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="hold-gate")

    with pytest.raises(AppException) as exc_info:
        hold_service.create_hold(
            db_session,
            member_id=1,
            schedule_id=schedule_id,
            seat_ids=[seat_ids[0]],
            entry_ticket=None,
        )
    assert exc_info.value.error_code == ErrorCode.QUEUE_ENTRY_TICKET_MISSING


def test_two_concurrent_holds_on_same_seat_only_one_succeeds(db_session):
    """가장 중요한 테스트: 같은 좌석에 대한 동시 요청 -> 정확히 1건만 성공."""
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="hold-race")
    target_seat = seat_ids[0]

    successes = 0
    failures = 0
    for member_id in range(1, 6):  # 5명이 같은 좌석을 동시에 노린다고 가정
        try:
            hold_service.create_hold(
                db_session,
                member_id=member_id,
                schedule_id=schedule_id,
                seat_ids=[target_seat],
                entry_ticket=None,
            )
            successes += 1
        except AppException as e:
            assert e.error_code == ErrorCode.RESV_SEAT_ALREADY_HELD
            failures += 1

    assert successes == 1
    assert failures == 4


def test_release_hold_success_returns_seat_to_available(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="release-ok")
    result = hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )

    hold_service.release_hold(db_session, hold_id=result.hold_id, member_id=1)

    hold_log = repository.get_seat_hold_log(db_session, result.hold_id)
    assert hold_log.status == "RELEASED"
    assert hold_log.released_at is not None

    seat = repository.get_seats_for_hold(db_session, schedule_id=schedule_id, seat_ids=[seat_ids[0]])[0]
    assert seat.status == "AVAILABLE"

    # 해제 후에는 다른 사람이 같은 좌석을 다시 잡을 수 있어야 한다.
    reheld = hold_service.create_hold(
        db_session, member_id=2, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )
    assert reheld.seat_ids == [seat_ids[0]]


def test_release_hold_wrong_owner_returns_403(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="release-wrong-owner")
    result = hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )

    with pytest.raises(AppException) as exc_info:
        hold_service.release_hold(db_session, hold_id=result.hold_id, member_id=999)
    assert exc_info.value.error_code == ErrorCode.RESV_HOLD_OWNER_MISMATCH


def test_release_hold_already_released_returns_expired(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="release-twice")
    result = hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )
    hold_service.release_hold(db_session, hold_id=result.hold_id, member_id=1)

    with pytest.raises(AppException) as exc_info:
        hold_service.release_hold(db_session, hold_id=result.hold_id, member_id=1)
    assert exc_info.value.error_code == ErrorCode.RESV_HOLD_EXPIRED


def test_get_hold_success_returns_remaining_seconds(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="get-ok")
    result = hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )

    detail = hold_service.get_hold(hold_id=result.hold_id, member_id=1)

    assert detail.seat_ids == [seat_ids[0]]
    assert detail.remaining_seconds > 0
    assert detail.remaining_seconds <= get_settings().hold_ttl_sec


def test_get_hold_wrong_owner_returns_403(db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="get-wrong-owner")
    result = hold_service.create_hold(
        db_session, member_id=1, schedule_id=schedule_id, seat_ids=[seat_ids[0]], entry_ticket=None
    )

    with pytest.raises(AppException) as exc_info:
        hold_service.get_hold(hold_id=result.hold_id, member_id=999)
    assert exc_info.value.error_code == ErrorCode.RESV_HOLD_OWNER_MISMATCH


def test_get_hold_nonexistent_returns_404():
    with pytest.raises(AppException) as exc_info:
        hold_service.get_hold(hold_id="no-such-hold", member_id=1)
    assert exc_info.value.error_code == ErrorCode.RESV_HOLD_NOT_FOUND
