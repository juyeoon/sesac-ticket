"""
[모듈] api/tests/test_queue.py
[담당] A
[역할] 대기열 진입(TRF-001) → queueToken 기반 순번 조회(TRF-002, 인증 불필요) →
       방출 후 entryTicket 발급 확인.

[구현할 것]
- test_three_members_enter_and_get_sequential_positions
- test_status_with_unknown_token_returns_404
- test_status_requires_no_auth_header
- test_dispatch_promotes_to_ready_with_entry_ticket

[의존]
- tests.conftest (client 픽스처)
- app.workers.queue_dispatcher.dispatch_once

[호출자]
- pytest

[주의]
- performance_id/schedule_id는 테스트마다 서로 겹치지 않는 값을 쓴다. Valkey
  Sorted Set이 테스트 세션 전체에서 공유되는 fakeredis 인스턴스 위에 있기 때문.
"""

from app.workers.queue_dispatcher import dispatch_once


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


def test_three_members_enter_and_get_sequential_positions(client):
    performance_id, schedule_id = 1, 101
    headers_list = [
        _signup_and_login(client, f"queue-enter-{i}@test.com") for i in range(1, 4)
    ]

    positions = []
    for headers in headers_list:
        response = client.post(
            "/api/v1/queue/enter",
            json={"performanceId": performance_id, "scheduleId": schedule_id},
            headers=headers,
        )
        assert response.status_code == 200
        positions.append(response.json()["position"])

    assert positions == [1, 2, 3]


def test_status_with_unknown_token_returns_404(client):
    response = client.get("/api/v1/queue/no-such-token/status")
    assert response.status_code == 404
    assert response.json()["errorCode"] == "QUEUE_NOT_ENTERED"


def test_status_requires_no_auth_header(client):
    performance_id, schedule_id = 2, 202
    headers = _signup_and_login(client, "queue-noauth@test.com")

    enter_response = client.post(
        "/api/v1/queue/enter",
        json={"performanceId": performance_id, "scheduleId": schedule_id},
        headers=headers,
    )
    token = enter_response.json()["queueToken"]

    # Authorization 헤더 없이도 조회가 되어야 한다 (설계서: 인증 불필요).
    status_response = client.get(f"/api/v1/queue/{token}/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "WAITING"
    assert status_response.json()["position"] == 1


def test_dispatch_promotes_to_ready_with_entry_ticket(client):
    performance_id, schedule_id = 3, 303
    headers = _signup_and_login(client, "queue-ready@test.com")

    enter_response = client.post(
        "/api/v1/queue/enter",
        json={"performanceId": performance_id, "scheduleId": schedule_id},
        headers=headers,
    )
    token = enter_response.json()["queueToken"]

    dispatched_count = dispatch_once(performance_id, schedule_id)
    assert dispatched_count == 1

    status_response = client.get(f"/api/v1/queue/{token}/status")
    assert status_response.status_code == 200
    body = status_response.json()
    assert body["status"] == "READY"
    assert body["entryTicket"] is not None
