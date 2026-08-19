"""
[모듈] api/tests/test_auth.py
[담당] A
[역할] 가입 → 로그인 → 재발급(쿠키) → 로그아웃 흐름 테스트.

[구현할 것]
- test_signup_success
- test_signup_duplicate_email_returns_409
- test_login_wrong_password_returns_401
- test_full_auth_flow (로그인→재발급→로그아웃→로그아웃 후 재발급 거부)

[의존]
- tests.conftest (client 픽스처)

[호출자]
- pytest

[주의]
- refreshToken은 응답 바디가 아니라 HttpOnly 쿠키로 온다. TestClient(httpx)는
  같은 client 인스턴스 안에서 쿠키를 자동으로 유지하므로, 로그인 후 별도로
  쿠키를 넘기지 않아도 refresh/logout 호출에 자동 포함된다.
"""


def test_signup_success(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "signup1@test.com", "password": "password123", "nickname": "nick1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["userId"], int)


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
    login_body = login_response.json()
    assert "accessToken" in login_body
    assert "refreshToken" not in login_body  # 바디에 노출되면 안 됨
    assert "refreshToken" in client.cookies  # 대신 HttpOnly 쿠키로 발급됨

    access_token = login_body["accessToken"]
    headers = {"Authorization": f"Bearer {access_token}"}

    refresh_response = client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200
    assert "accessToken" in refresh_response.json()

    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["loggedOut"] is True

    refresh_after_logout = client.post("/api/v1/auth/refresh")
    assert refresh_after_logout.status_code == 401
    assert refresh_after_logout.json()["errorCode"] == "AUTH_TOKEN_INVALID"
