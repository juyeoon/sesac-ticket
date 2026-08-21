"""
[모듈] api/tests/test_reservation_admin_list.py
[담당] A
[역할] 관리자 전용 전체 예매 목록 조회(GET /reservations/list) 테스트.

[구현할 것]
- test_list_all_reservations_returns_all_members_reservations
- test_list_all_reservations_includes_member_performance_schedule_seats
- test_list_all_reservations_requires_admin

[의존]
- tests.conftest (client, db_session 픽스처)
- app.domains.reservation.hold_service, service

[호출자]
- pytest
"""

from datetime import date, time

import pytest

from app.core.config import get_settings
from app.core.security import hash_password
from app.domains.admin.model import Admin
from app.domains.member.model import Member
from app.domains.performance.model import Category, Performance, Schedule
from app.domains.reservation import hold_service, service
from app.domains.reservation.model import ScheduleSeat
from app.domains.venue.model import Venue, VenueSeat


@pytest.fixture(autouse=True)
def _bypass_queue_gate(monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)


def _create_member(db_session, *, email: str) -> Member:
    member = Member(email=email, password_hash=hash_password("password123"), nickname="관리자목록검증")
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)
    return member


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


def _create_reservation(db_session, *, title: str, member: Member):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title=title)
    hold_result = hold_service.create_hold(
        db_session, member_id=member.id, schedule_id=schedule_id, seat_ids=seat_ids, entry_ticket=None
    )
    return service.create_reservation(
        db_session, member_id=member.id, hold_id=hold_result.hold_id, depositor_name="홍길동"
    )


def test_list_all_reservations_returns_all_members_reservations(db_session):
    member_a = _create_member(db_session, email="admin-list-a@test.com")
    member_b = _create_member(db_session, email="admin-list-b@test.com")
    _create_reservation(db_session, title="admin-list-1", member=member_a)
    _create_reservation(db_session, title="admin-list-2", member=member_b)

    items = service.list_all_reservations_admin(db_session)

    member_ids = {item.member.member_id for item in items}
    assert member_a.id in member_ids
    assert member_b.id in member_ids


def test_list_all_reservations_includes_member_performance_schedule_seats(db_session):
    member = _create_member(db_session, email="admin-list-detail@test.com")
    created = _create_reservation(db_session, title="admin-list-detail", member=member)

    items = service.list_all_reservations_admin(db_session)
    item = next(i for i in items if i.reservation_id == created.reservation_id)

    assert item.member.member_id == member.id
    assert item.member.email == "admin-list-detail@test.com"
    assert item.performance.title == "admin-list-detail"
    assert item.schedule.schedule_id is not None
    assert len(item.seats) == 1
    assert item.depositor_name == "홍길동"
    assert item.status == "PENDING_PAYMENT"


def test_list_all_reservations_requires_admin(client, db_session):
    def _signup_and_login(email: str) -> dict:
        client.post(
            "/api/v1/auth/signup",
            json={"email": email, "password": "password123", "nickname": "테스터"},
        )
        response = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
        return {"Authorization": f"Bearer {response.json()['accessToken']}"}

    member_headers = _signup_and_login("admin-list-non-admin@test.com")
    response = client.get("/api/v1/reservations/list", headers=member_headers)
    assert response.status_code == 401

    admin = Admin(
        admin_id="admin-list-admin",
        password_hash=hash_password("adminpass123"),
        name="테스트 관리자",
        role="SUPER",
    )
    db_session.add(admin)
    db_session.commit()
    admin_login = client.post(
        "/api/v1/admin/auth/login",
        json={"adminId": "admin-list-admin", "password": "adminpass123"},
    )
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['accessToken']}"}
    response = client.get("/api/v1/reservations/list", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
