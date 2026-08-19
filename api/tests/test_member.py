"""
[모듈] api/tests/test_member.py
[담당] A
[역할] 내 정보 조회/수정(본인인증), 회원 탈퇴(소프트 삭제) 및 탈퇴 후 접근 차단 테스트.
       api 설계서 AUTH-002, 008, 009에 대응.

[구현할 것]
- test_get_my_info
- test_update_my_info_requires_verification_code
- test_update_my_info_with_valid_code
- test_withdraw_wrong_password_returns_401_and_stays_active
- test_withdraw_then_token_and_login_are_blocked

[의존]
- tests.conftest (client 픽스처)
- app.domains.auth.repository (인증 코드를 테스트에서 직접 조회하기 위함)

[호출자]
- pytest
"""

from app.domains.auth import repository as auth_repository


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


def test_get_my_info(client):
    headers = _signup_and_login(client, "member-get@test.com")

    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "member-get@test.com"
    assert "password_hash" not in body


def test_update_my_info_requires_verification_code(client):
    email = "member-update-noverify@test.com"
    headers = _signup_and_login(client, email)

    response = client.patch(
        "/api/v1/users/me",
        json={"nickname": "newnick", "verificationCode": "000000"},
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json()["errorCode"] == "AUTH_EMAIL_VERIFICATION_CODE_INVALID"


def test_update_my_info_with_valid_code(client):
    email = "member-update@test.com"
    headers = _signup_and_login(client, email)

    client.post("/api/v1/auth/email/verify-request", json={"email": email})
    code = auth_repository.get_email_verification_code(email)

    response = client.patch(
        "/api/v1/users/me",
        json={"nickname": "newnick", "ageRange": "30대", "verificationCode": code},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["updated"] is True

    profile = client.get("/api/v1/users/me", headers=headers)
    assert profile.json()["nickname"] == "newnick"
    assert profile.json()["ageRange"] == "30대"

    # 인증 코드는 1회용이라 재사용하면 실패한다.
    reuse_response = client.patch(
        "/api/v1/users/me",
        json={"nickname": "anothernick", "verificationCode": code},
        headers=headers,
    )
    assert reuse_response.status_code == 400


def test_withdraw_wrong_password_returns_401_and_stays_active(client):
    headers = _signup_and_login(client, "member-withdraw-fail@test.com")

    response = client.request(
        "DELETE", "/api/v1/users/me", json={"password": "wrong"}, headers=headers
    )
    assert response.status_code == 401
    assert response.json()["errorCode"] == "AUTH_INVALID_CREDENTIALS"

    still_active = client.get("/api/v1/users/me", headers=headers)
    assert still_active.json()["status"] == "ACTIVE"


def test_withdraw_then_token_and_login_are_blocked(client):
    email = "member-withdraw@test.com"
    headers = _signup_and_login(client, email)

    response = client.request(
        "DELETE", "/api/v1/users/me", json={"password": "password123"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    # 탈퇴 시점에 아직 만료 전인 access 토큰도 즉시 거부되어야 한다.
    blocked = client.get("/api/v1/users/me", headers=headers)
    assert blocked.status_code == 403
    assert blocked.json()["errorCode"] == "AUTH_MEMBER_WITHDRAWN"

    login_after_withdraw = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "password123"}
    )
    assert login_after_withdraw.status_code == 403
    assert login_after_withdraw.json()["errorCode"] == "AUTH_MEMBER_WITHDRAWN"
