"""
[모듈] api/tests/test_reservation_router.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 예매 도메인 라우터 HTTP 엔드투엔드 테스트 (RESV-002~007, 012, 013).
       서비스 계층은 이미 각 단계별 테스트로 검증됐으므로, 여기서는 라우팅/인증/
       직렬화(camelCase)가 올바르게 연결됐는지에 집중한다.

[구현할 것]
- test_full_reservation_flow_via_http
    좌석상태조회 → 선점 → 선점상태조회 → 해제 → 재선점 → 예매생성 → 관리자확정
    → 예매상세조회 → 내예매목록조회 를 실제 HTTP 요청으로 전부 통과시킨다.
- test_seat_status_requires_auth
- test_hold_requires_auth
- test_confirm_reservation_requires_admin

[의존]
- tests.conftest (client, db_session 픽스처)

[호출자]
- pytest
"""

from datetime import date, time

from app.core.config import get_settings
from app.core.security import hash_password
from app.domains.admin.model import Admin
from app.domains.performance.model import Category, Performance, Schedule
from app.domains.venue.model import Venue, VenueSeat
from app.domains.reservation.model import ScheduleSeat


def _signup_and_login(client, email: str) -> dict:
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "nickname": "nick"},
    )
    response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "password123"}
    )
    access_token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {access_token}"}


def _create_admin_headers(client, db_session, admin_id: str) -> dict:
    admin = Admin(
        admin_id=admin_id,
        password_hash=hash_password("adminpass123"),
        name="테스트 관리자",
        role="SUPER",
    )
    db_session.add(admin)
    db_session.commit()

    response = client.post(
        "/api/v1/admin/auth/login",
        json={"adminId": admin_id, "password": "adminpass123"},
    )
    access_token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {access_token}"}


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


def test_full_reservation_flow_via_http(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)
    headers = _signup_and_login(client, "resv-flow@test.com")
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="router-flow")

    status_response = client.get(f"/api/v1/schedules/{schedule_id}/seats", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()[0]["status"] == "AVAILABLE"

    hold_response = client.post(
        "/api/v1/seats/hold",
        headers=headers,
        json={"scheduleId": schedule_id, "seatIds": seat_ids},
    )
    assert hold_response.status_code == 200
    hold_body = hold_response.json()
    hold_id = hold_body["holdId"]
    assert hold_body["seatIds"] == seat_ids

    get_hold_response = client.get(f"/api/v1/seats/hold/{hold_id}", headers=headers)
    assert get_hold_response.status_code == 200
    assert get_hold_response.json()["remainingSeconds"] > 0

    release_response = client.delete(f"/api/v1/seats/hold/{hold_id}", headers=headers)
    assert release_response.status_code == 200
    assert release_response.json()["released"] is True

    re_hold_response = client.post(
        "/api/v1/seats/hold",
        headers=headers,
        json={"scheduleId": schedule_id, "seatIds": seat_ids},
    )
    assert re_hold_response.status_code == 200
    hold_id = re_hold_response.json()["holdId"]

    create_reservation_response = client.post(
        "/api/v1/reservations/bank-transfer",
        headers=headers,
        json={"holdId": hold_id, "depositorName": "홍길동"},
    )
    assert create_reservation_response.status_code == 201
    reservation_body = create_reservation_response.json()
    assert reservation_body["status"] == "PENDING_PAYMENT"
    reservation_id = reservation_body["reservationId"]

    admin_headers = _create_admin_headers(client, db_session, "resv-flow-admin")
    confirm_response = client.post(
        f"/api/v1/reservations/bank-transfer/{reservation_id}/confirm",
        headers=admin_headers,
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["status"] == "CONFIRMED"

    detail_response = client.get(
        f"/api/v1/reservations/bank-transfer/{reservation_id}", headers=headers
    )
    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["performance"]["title"] == "router-flow"
    assert detail_body["status"] == "CONFIRMED"

    my_list_response = client.get("/api/v1/users/me/reservations", headers=headers)
    assert my_list_response.status_code == 200
    my_list_body = my_list_response.json()
    assert my_list_body["totalElements"] == 1
    assert my_list_body["content"][0]["reservationId"] == reservation_id


def test_seat_status_requires_auth(client, db_session):
    schedule_id, _ = _create_schedule_with_seats(db_session, title="router-no-auth-status")

    response = client.get(f"/api/v1/schedules/{schedule_id}/seats")
    assert response.status_code == 401


def test_hold_requires_auth(client, db_session):
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="router-no-auth-hold")

    response = client.post(
        "/api/v1/seats/hold", json={"scheduleId": schedule_id, "seatIds": seat_ids}
    )
    assert response.status_code == 401


def test_confirm_reservation_requires_admin(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)
    headers = _signup_and_login(client, "resv-non-admin@test.com")
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="router-non-admin")

    hold_response = client.post(
        "/api/v1/seats/hold",
        headers=headers,
        json={"scheduleId": schedule_id, "seatIds": seat_ids},
    )
    hold_id = hold_response.json()["holdId"]
    create_response = client.post(
        "/api/v1/reservations/bank-transfer",
        headers=headers,
        json={"holdId": hold_id, "depositorName": "홍길동"},
    )
    reservation_id = create_response.json()["reservationId"]

    confirm_response = client.post(
        f"/api/v1/reservations/bank-transfer/{reservation_id}/confirm", headers=headers
    )
    assert confirm_response.status_code == 401
