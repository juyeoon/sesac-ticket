"""
[모듈] api/tests/test_queue.py
[담당] A
[역할] 3명 진입 → 순번 1·2·3 확인 → 방출 후 entryTicket 발급 확인.

[구현할 것]
- test_three_members_enter_and_get_sequential_positions
- test_status_without_entering_returns_404
- test_dispatch_promotes_to_ready_with_entry_ticket

[의존]
- tests.conftest (client 픽스처)
- app.workers.queue_dispatcher.dispatch_once

[호출자]
- pytest

[주의]
- schedule_id는 테스트마다 서로 겹치지 않는 값을 쓴다. Valkey Sorted Set이
  테스트 세션 전체에서 공유되는 fakeredis 인스턴스 위에 있기 때문.
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
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_three_members_enter_and_get_sequential_positions(client):
    schedule_id = 101
    headers_list = [
        _signup_and_login(client, f"queue-enter-{i}@test.com") for i in range(1, 4)
    ]

    positions = []
    for headers in headers_list:
        response = client.post(
            "/api/v1/queue/enter", json={"schedule_id": schedule_id}, headers=headers
        )
        assert response.status_code == 200
        positions.append(response.json()["position"])

    assert positions == [1, 2, 3]


def test_status_without_entering_returns_404(client):
    headers = _signup_and_login(client, "queue-none@test.com")

    response = client.get(
        "/api/v1/queue/status", params={"schedule_id": 999}, headers=headers
    )
    assert response.status_code == 404
    assert response.json()["errorCode"] == "QUEUE_NOT_ENTERED"


def test_dispatch_promotes_to_ready_with_entry_ticket(client):
    schedule_id = 202
    headers = _signup_and_login(client, "queue-ready@test.com")
    client.post("/api/v1/queue/enter", json={"schedule_id": schedule_id}, headers=headers)

    dispatched_count = dispatch_once(schedule_id)
    assert dispatched_count == 1

    response = client.get(
        "/api/v1/queue/status", params={"schedule_id": schedule_id}, headers=headers
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "READY"
    assert body["entry_ticket"] is not None
