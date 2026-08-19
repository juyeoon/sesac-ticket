"""
[모듈] api/tests/test_system.py
[담당] A
[역할] 헬스체크(SYS-001/002) + 버전 조회(SYS-003) 테스트.

[구현할 것]
- test_health_live_returns_up
- test_health_ready_returns_up_when_dependencies_ok
- test_version_default
- test_version_with_valid_platform
- test_version_with_invalid_platform_returns_400

[의존]
- tests.conftest (client 픽스처)

[호출자]
- pytest
"""


def test_health_live_returns_up(client):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_health_ready_returns_up_when_dependencies_ok(client):
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "UP"
    assert body["checks"] == {"db": "UP", "valkey": "UP"}


def test_version_default(client):
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    body = response.json()
    assert "apiVersion" in body
    assert set(body["app"].keys()) == {
        "latestVersion",
        "minRequiredVersion",
        "forceUpdate",
        "updateUrl",
    }


def test_version_with_valid_platform(client):
    for platform in ["ios", "android", "web"]:
        response = client.get("/api/v1/version", params={"platform": platform})
        assert response.status_code == 200


def test_version_with_invalid_platform_returns_400(client):
    response = client.get("/api/v1/version", params={"platform": "windows"})
    assert response.status_code == 400
