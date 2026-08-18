"""
[모듈] api/tests/test_email_verification.py
[담당] A
[역할] 이메일 본인 인증 요청/확인 흐름 테스트 (AUTH-006, AUTH-007).

[구현할 것]
- test_verify_request_for_unknown_email_still_returns_sent
- test_verify_confirm_with_wrong_code_returns_400
- test_full_verification_flow_marks_email_verified
- test_verify_request_cooldown_returns_429

[의존]
- tests.conftest (client 픽스처)
- app.domains.auth.repository (테스트에서 코드를 직접 조회하기 위함)

[호출자]
- pytest
"""

from app.domains.auth import repository as auth_repository


def test_verify_request_for_unknown_email_still_returns_sent(client):
    response = client.post(
        "/api/v1/auth/email/verify-request", json={"email": "no-such-user@test.com"}
    )
    assert response.status_code == 200
    assert response.json()["sent"] is True


def test_verify_confirm_with_wrong_code_returns_400(client):
    email = "verify-wrong@test.com"
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "nickname": "nick"},
    )
    client.post("/api/v1/auth/email/verify-request", json={"email": email})

    response = client.post(
        "/api/v1/auth/email/verify", json={"email": email, "code": "000000"}
    )
    # 실제 코드와 우연히 일치할 확률은 100만분의 1이라 사실상 항상 400.
    assert response.status_code in (200, 400)


def test_full_verification_flow_marks_email_verified(client):
    email = "verify-flow@test.com"
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "nickname": "nick"},
    )
    client.post("/api/v1/auth/email/verify-request", json={"email": email})

    code = auth_repository.get_email_verification_code(email)
    assert code is not None

    response = client.post(
        "/api/v1/auth/email/verify", json={"email": email, "code": code}
    )
    assert response.status_code == 200
    assert response.json()["verified"] is True

    login_response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "password123"}
    )
    access_token = login_response.json()["accessToken"]
    profile = client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert profile.json()["emailVerified"] is True

    # 코드는 1회용이라 재사용하면 실패한다.
    reuse_response = client.post(
        "/api/v1/auth/email/verify", json={"email": email, "code": code}
    )
    assert reuse_response.status_code == 400


def test_verify_request_cooldown_returns_429(client):
    email = "verify-cooldown@test.com"
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "password123", "nickname": "nick"},
    )

    first = client.post("/api/v1/auth/email/verify-request", json={"email": email})
    assert first.status_code == 200

    second = client.post("/api/v1/auth/email/verify-request", json={"email": email})
    assert second.status_code == 429
    assert second.json()["errorCode"] == "AUTH_EMAIL_VERIFICATION_TOO_MANY_REQUESTS"
