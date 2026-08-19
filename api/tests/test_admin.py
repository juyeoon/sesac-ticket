"""
[모듈] api/tests/test_admin.py
[담당] A
[역할] 관리자 로그인/토큰재발급 흐름 테스트 (ADMIN-007/008).

[구현할 것]
- test_admin_login_success_sets_refresh_cookie
- test_admin_login_wrong_password_returns_401
- test_admin_refresh_flow
- test_admin_refresh_token_is_separate_from_member_cookie

[의존]
- tests.conftest (client, db_session 픽스처)
- app.domains.admin.model, app.core.security (테스트용 관리자 계정 직접 생성)

[호출자]
- pytest
"""

from app.core.security import hash_password
from app.domains.admin.model import Admin


def _create_admin(db_session, admin_id: str, password: str) -> Admin:
    admin = Admin(
        admin_id=admin_id,
        password_hash=hash_password(password),
        name="테스트 관리자",
        role="SUPER",
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


def test_admin_login_success_sets_refresh_cookie(client, db_session):
    _create_admin(db_session, "admin-login", "adminpass123")

    response = client.post(
        "/api/v1/admin/auth/login",
        json={"adminId": "admin-login", "password": "adminpass123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "accessToken" in body
    assert body["tokenType"] == "Bearer"
    assert "adminRefreshToken" not in body
    assert "adminRefreshToken" in client.cookies


def test_admin_login_wrong_password_returns_401(client, db_session):
    _create_admin(db_session, "admin-wrong", "adminpass123")

    response = client.post(
        "/api/v1/admin/auth/login",
        json={"adminId": "admin-wrong", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["errorCode"] == "AUTH_INVALID_CREDENTIALS"


def test_admin_refresh_flow(client, db_session):
    _create_admin(db_session, "admin-refresh", "adminpass123")
    client.post(
        "/api/v1/admin/auth/login",
        json={"adminId": "admin-refresh", "password": "adminpass123"},
    )

    refresh_response = client.post("/api/v1/admin/auth/refresh")
    assert refresh_response.status_code == 200
    assert "accessToken" in refresh_response.json()


def test_admin_refresh_without_cookie_returns_401(client):
    # 이 client 인스턴스가 admin 로그인을 한 적이 없다는 걸 보장하기 위해 새 처리.
    response = client.post("/api/v1/admin/auth/refresh")
    assert response.status_code == 401
    assert response.json()["errorCode"] == "AUTH_TOKEN_INVALID"
