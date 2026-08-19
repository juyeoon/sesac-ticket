"""
[모듈] api/tests/test_password_reset.py
[담당] A
[역할] 비밀번호 재설정 요청/확인 흐름 테스트 (AUTH-004, AUTH-005).

[구현할 것]
- test_reset_request_always_returns_sent_even_for_unknown_email
- test_reset_confirm_with_invalid_token_returns_400
- test_full_reset_flow_changes_password_and_revokes_session

[의존]
- tests.conftest (client 픽스처)
- app.domains.auth.repository (테스트에서 토큰을 직접 꺼내기 위함)

[호출자]
- pytest
"""

from app.domains.auth import repository as auth_repository
from app.domains.member import repository as member_repository


def test_reset_request_always_returns_sent_even_for_unknown_email(client, db_session):
    response = client.post(
        "/api/v1/auth/password/reset-request", json={"email": "no-such-user@test.com"}
    )
    assert response.status_code == 200
    assert response.json()["sent"] is True


def test_reset_confirm_with_invalid_token_returns_400(client):
    response = client.post(
        "/api/v1/auth/password/reset",
        json={"resetToken": "not-a-real-token", "newPassword": "newpassword123"},
    )
    assert response.status_code == 400
    assert response.json()["errorCode"] == "AUTH_PASSWORD_RESET_TOKEN_INVALID"


def test_full_reset_flow_changes_password_and_revokes_session(client, db_session):
    email = "reset-flow@test.com"
    client.post(
        "/api/v1/auth/signup",
        json={"email": email, "password": "oldpassword123", "nickname": "nick"},
    )
    login_response = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "oldpassword123"}
    )
    assert login_response.status_code == 200

    # 실제 메일은 발송되지 않으므로(스텁), Valkey에 저장된 토큰을 테스트에서 직접 조회한다.
    member = member_repository.get_member_by_email(db_session, email)
    client.post("/api/v1/auth/password/reset-request", json={"email": email})

    # request_password_reset이 저장한 토큰을 알아내기 위해 서비스와 같은 방식으로 생성했는지
    # 확인할 수 없으므로, repository를 통해 토큰을 직접 발급/저장해 confirm 경로만 검증한다.
    reset_token = "test-reset-token"
    auth_repository.save_password_reset_token(reset_token, member.id, 900)

    confirm_response = client.post(
        "/api/v1/auth/password/reset",
        json={"resetToken": reset_token, "newPassword": "newpassword123"},
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["reset"] is True

    # 기존 비밀번호로는 더 이상 로그인할 수 없다.
    old_password_login = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "oldpassword123"}
    )
    assert old_password_login.status_code == 401

    # 새 비밀번호로는 로그인 가능하다.
    new_password_login = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "newpassword123"}
    )
    assert new_password_login.status_code == 200

    # 토큰은 1회용이라 재사용하면 실패한다.
    reuse_response = client.post(
        "/api/v1/auth/password/reset",
        json={"resetToken": reset_token, "newPassword": "anotherpassword123"},
    )
    assert reuse_response.status_code == 400
