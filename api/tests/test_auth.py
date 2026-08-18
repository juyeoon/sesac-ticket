"""
[모듈] api/tests/test_auth.py
[담당] A
[역할] 가입 → 로그인 → 재발급 → 로그아웃 흐름 테스트.

[구현할 것]
- test_signup_success
- test_signup_duplicate_email_returns_409
- test_login_wrong_password_returns_401
- test_full_auth_flow (로그인→재발급→로그아웃→로그아웃 후 재발급 거부)

[의존]
- tests.conftest (client 픽스처)

[호출자]
- pytest
"""


def test_signup_success(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "signup1@test.com", "password": "password123", "nickname": "nick1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "signup1@test.com"
    assert "password_hash" not in body


def test_signup_duplicate_email_returns_409(client):
    payload = {"email": "dup@test.com", "password": "password123", "nickname": "nick"}
    first = client.post("/api/v1/auth/signup", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/auth/signup", json=payload)
    assert second.status_code == 409
    assert second.json()["errorCode"] == "AUTH_EMAIL_ALREADY_EXISTS"


def test_login_wrong_password_returns_401(client):
    client.post(
        "/api/v1/auth/signup",
        json={"email": "login1@test.com", "password": "password123", "nickname": "nick"},
    )

    response = client.post(
        "/api/v1/auth/login", json={"email": "login1@test.com", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["errorCode"] == "AUTH_INVALID_CREDENTIALS"


def test_full_auth_flow(client):
    client.post(
        "/api/v1/auth/signup",
        json={"email": "flow@test.com", "password": "password123", "nickname": "nick"},
    )

    login_response = client.post(
        "/api/v1/auth/login", json={"email": "flow@test.com", "password": "password123"}
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    refresh_response = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()

    logout_response = client.post(
        "/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
    )
    assert logout_response.status_code == 204

    refresh_after_logout = client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_after_logout.status_code == 401
    assert refresh_after_logout.json()["errorCode"] == "AUTH_TOKEN_INVALID"
