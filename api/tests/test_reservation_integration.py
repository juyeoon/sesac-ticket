"""
[모듈] api/tests/test_reservation_integration.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 예매 도메인 통합 테스트 — 각 단계에서 서비스 레벨로 검증한 로직들이
       실제 HTTP 경로 + 여러 컴포넌트(라우터/서비스/hold_sweeper/Valkey)를
       가로질러도 여전히 성립하는지 확인한다. RESV 전 API 대상, 9단계.

[구현할 것]
- test_double_hold_same_seat_returns_409_via_http
- test_create_reservation_with_released_hold_returns_410_via_http
- test_get_reservation_detail_wrong_owner_returns_403_via_http
- test_confirm_already_confirmed_reservation_returns_409_via_http
- test_confirm_nonexistent_reservation_returns_404_via_http
- test_hold_sweeper_reopens_seat_after_expiry_then_visible_via_http

[의존]
- tests.conftest (client, db_session 픽스처)
- app.workers.hold_sweeper

[호출자]
- pytest
"""

from datetime import date, time, timedelta

from app.core.config import get_settings
from app.domains.performance.model import Category, Performance, Schedule
from app.domains.reservation import repository
from app.domains.reservation.model import ScheduleSeat
from app.domains.venue.model import Venue, VenueSeat
from app.workers.hold_sweeper import sweep_expired_holds


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


def test_double_hold_same_seat_returns_409_via_http(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)
    headers_a = _signup_and_login(client, "integration-double-hold-a@test.com")
    headers_b = _signup_and_login(client, "integration-double-hold-b@test.com")
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="integration-double-hold")

    first = client.post(
        "/api/v1/seats/hold", headers=headers_a, json={"scheduleId": schedule_id, "seatIds": seat_ids}
    )
    assert first.status_code == 200

    second = client.post(
        "/api/v1/seats/hold", headers=headers_b, json={"scheduleId": schedule_id, "seatIds": seat_ids}
    )
    assert second.status_code == 409
    assert second.json()["errorCode"] == "RESV_SEAT_ALREADY_HELD"


def test_create_reservation_with_released_hold_returns_410_via_http(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)
    headers = _signup_and_login(client, "integration-released-hold@test.com")
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="integration-released-hold")

    hold_response = client.post(
        "/api/v1/seats/hold", headers=headers, json={"scheduleId": schedule_id, "seatIds": seat_ids}
    )
    hold_id = hold_response.json()["holdId"]

    release_response = client.delete(f"/api/v1/seats/hold/{hold_id}", headers=headers)
    assert release_response.status_code == 200

    create_response = client.post(
        "/api/v1/reservations/bank-transfer",
        headers=headers,
        json={"holdId": hold_id, "depositorName": "홍길동"},
    )
    assert create_response.status_code == 410
    assert create_response.json()["errorCode"] == "RESV_HOLD_EXPIRED"


def test_get_reservation_detail_wrong_owner_returns_403_via_http(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)
    owner_headers = _signup_and_login(client, "integration-owner@test.com")
    stranger_headers = _signup_and_login(client, "integration-stranger@test.com")
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="integration-wrong-owner")

    hold_response = client.post(
        "/api/v1/seats/hold", headers=owner_headers, json={"scheduleId": schedule_id, "seatIds": seat_ids}
    )
    hold_id = hold_response.json()["holdId"]

    create_response = client.post(
        "/api/v1/reservations/bank-transfer",
        headers=owner_headers,
        json={"holdId": hold_id, "depositorName": "홍길동"},
    )
    reservation_id = create_response.json()["reservationId"]

    detail_response = client.get(
        f"/api/v1/reservations/bank-transfer/{reservation_id}", headers=stranger_headers
    )
    assert detail_response.status_code == 403
    assert detail_response.json()["errorCode"] == "RESV_OWNER_MISMATCH"


def test_confirm_already_confirmed_reservation_returns_409_via_http(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)
    headers = _signup_and_login(client, "integration-double-confirm@test.com")
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="integration-double-confirm")

    hold_response = client.post(
        "/api/v1/seats/hold", headers=headers, json={"scheduleId": schedule_id, "seatIds": seat_ids}
    )
    hold_id = hold_response.json()["holdId"]
    create_response = client.post(
        "/api/v1/reservations/bank-transfer",
        headers=headers,
        json={"holdId": hold_id, "depositorName": "홍길동"},
    )
    reservation_id = create_response.json()["reservationId"]

    from app.core.security import hash_password
    from app.domains.admin.model import Admin

    admin = Admin(
        admin_id="integration-double-confirm-admin",
        password_hash=hash_password("adminpass123"),
        name="테스트 관리자",
        role="SUPER",
    )
    db_session.add(admin)
    db_session.commit()
    admin_login = client.post(
        "/api/v1/admin/auth/login",
        json={"adminId": "integration-double-confirm-admin", "password": "adminpass123"},
    )
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['accessToken']}"}

    first_confirm = client.post(
        f"/api/v1/reservations/bank-transfer/{reservation_id}/confirm", headers=admin_headers
    )
    assert first_confirm.status_code == 200

    second_confirm = client.post(
        f"/api/v1/reservations/bank-transfer/{reservation_id}/confirm", headers=admin_headers
    )
    assert second_confirm.status_code == 409
    assert second_confirm.json()["errorCode"] == "RESV_INVALID_STATUS_TRANSITION"


def test_confirm_nonexistent_reservation_returns_404_via_http(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)
    from app.core.security import hash_password
    from app.domains.admin.model import Admin

    admin = Admin(
        admin_id="integration-404-confirm-admin",
        password_hash=hash_password("adminpass123"),
        name="테스트 관리자",
        role="SUPER",
    )
    db_session.add(admin)
    db_session.commit()
    admin_login = client.post(
        "/api/v1/admin/auth/login",
        json={"adminId": "integration-404-confirm-admin", "password": "adminpass123"},
    )
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['accessToken']}"}

    response = client.post(
        "/api/v1/reservations/bank-transfer/999999/confirm", headers=admin_headers
    )
    assert response.status_code == 404
    assert response.json()["errorCode"] == "RESV_NOT_FOUND"


def test_hold_sweeper_reopens_seat_after_expiry_then_visible_via_http(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "queue_enabled", False)
    headers = _signup_and_login(client, "integration-sweeper@test.com")
    schedule_id, seat_ids = _create_schedule_with_seats(db_session, title="integration-sweeper")

    hold_response = client.post(
        "/api/v1/seats/hold", headers=headers, json={"scheduleId": schedule_id, "seatIds": seat_ids}
    )
    hold_id = hold_response.json()["holdId"]

    status_before = client.get(f"/api/v1/schedules/{schedule_id}/seats", headers=headers)
    assert status_before.json()[0]["status"] == "HELD"

    hold_log = repository.get_seat_hold_log(db_session, hold_id)
    hold_log.expires_at = hold_log.expires_at - timedelta(days=1)
    db_session.commit()

    swept = sweep_expired_holds(db_session)
    assert swept == 1

    status_after = client.get(f"/api/v1/schedules/{schedule_id}/seats", headers=headers)
    assert status_after.json()[0]["status"] == "AVAILABLE"

    re_hold_response = client.post(
        "/api/v1/seats/hold", headers=headers, json={"scheduleId": schedule_id, "seatIds": seat_ids}
    )
    assert re_hold_response.status_code == 200
