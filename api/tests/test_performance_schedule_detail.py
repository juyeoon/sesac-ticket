"""
[모듈] api/tests/test_performance_schedule_detail.py
[담당] A (B가 일임 — 2026-08-20)
[역할] 회차 단건 조회(scheduleId → performanceId/venueId 역참조) 테스트.
       프론트Q-백엔드-답변.md #1에서 발견된 미구현 갭을 메우는 API.

[구현할 것]
- test_get_schedule_detail_returns_performance_and_venue_ids
- test_get_schedule_detail_includes_seat_grades
- test_get_schedule_detail_returns_404_for_missing_schedule

[의존]
- tests.conftest (client, db_session 픽스처)

[호출자]
- pytest
"""

from datetime import date, time

from app.domains.performance.model import Category, Performance, Schedule
from app.domains.reservation.model import ScheduleSeat
from app.domains.venue.model import Venue, VenueSeat


def _create_schedule(db_session, *, title: str):
    category = Category(name=f"cat-{title}", sort_order=0)
    venue = Venue(name=f"venue-{title}", address="서울시 어딘가")
    db_session.add_all([category, venue])
    db_session.flush()

    performance = Performance(
        title=title, category_id=category.id, venue_id=venue.id, status="ACTIVE"
    )
    db_session.add(performance)
    db_session.flush()

    schedule = Schedule(
        performance_id=performance.id,
        perf_date=date(2026, 9, 1),
        perf_time=time(19, 0),
        status="OPEN",
    )
    db_session.add(schedule)
    db_session.flush()

    venue_seat = VenueSeat(venue_id=venue.id, section="A", row_no="1", seat_no=1, grade="VIP")
    db_session.add(venue_seat)
    db_session.flush()

    db_session.add(
        ScheduleSeat(
            schedule_id=schedule.id,
            venue_seat_id=venue_seat.id,
            grade="VIP",
            price=100000,
            status="AVAILABLE",
        )
    )
    db_session.commit()

    return performance, venue, schedule


def test_get_schedule_detail_returns_performance_and_venue_ids(client, db_session):
    performance, venue, schedule = _create_schedule(db_session, title="schedule-detail-basic")

    response = client.get(f"/api/v1/schedules/{schedule.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["scheduleId"] == schedule.id
    assert body["performanceId"] == performance.id
    assert body["performanceTitle"] == "schedule-detail-basic"
    assert body["venueId"] == venue.id
    assert body["venueName"] == venue.name
    assert body["date"] == "2026-09-01"


def test_get_schedule_detail_includes_seat_grades(client, db_session):
    _, _, schedule = _create_schedule(db_session, title="schedule-detail-grades")

    response = client.get(f"/api/v1/schedules/{schedule.id}")

    body = response.json()
    assert body["seatGrades"] == [{"grade": "VIP", "price": 100000, "remaining": 1}]


def test_get_schedule_detail_returns_404_for_missing_schedule(client):
    response = client.get("/api/v1/schedules/999999")

    assert response.status_code == 404
    assert response.json()["errorCode"] == "PERF_SCHEDULE_NOT_FOUND"
