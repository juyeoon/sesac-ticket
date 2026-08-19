"""
[모듈] api/tests/test_favorites.py
[담당] A
[역할] 관심 공연 목록 조회/등록/삭제 테스트 (AUTH-010~012).

[구현할 것]
- test_add_favorite_then_appears_in_list
- test_add_favorite_for_missing_performance_returns_404
- test_add_favorite_twice_returns_409
- test_remove_favorite_not_registered_returns_404
- test_remove_favorite_then_disappears_from_list

[의존]
- tests.conftest (client, db_session 픽스처)

[호출자]
- pytest

[주의]
- B의 domains/performance ORM 모델을 그대로 사용해 테스트 데이터를 만든다
  (category_id/venue_id가 NOT NULL이라 Category/Venue도 함께 생성해야 함).
"""

from app.domains.performance.model import Category, Performance, PerformanceImage
from app.domains.venue.model import Venue


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


def _create_performance(db_session, title: str) -> int:
    category = Category(name=f"category-{title}", sort_order=0)
    venue = Venue(name=f"venue-{title}")
    db_session.add_all([category, venue])
    db_session.flush()

    performance = Performance(
        title=title,
        category_id=category.id,
        venue_id=venue.id,
        status="ACTIVE",
    )
    db_session.add(performance)
    db_session.commit()
    db_session.refresh(performance)
    return performance.id


def test_add_favorite_then_appears_in_list(client, db_session):
    headers = _signup_and_login(client, "favorite-add@test.com")
    performance_id = _create_performance(db_session, "테스트 공연 A")

    add_response = client.post(
        f"/api/v1/users/me/favorites/{performance_id}", headers=headers
    )
    assert add_response.status_code == 201
    assert add_response.json()["favorited"] is True

    list_response = client.get("/api/v1/users/me/favorites", headers=headers)
    assert list_response.status_code == 200
    body = list_response.json()
    assert body["totalElements"] == 1
    assert body["content"][0]["performanceId"] == performance_id
    assert body["content"][0]["title"] == "테스트 공연 A"


def test_add_favorite_for_missing_performance_returns_404(client):
    headers = _signup_and_login(client, "favorite-missing@test.com")

    response = client.post("/api/v1/users/me/favorites/999999", headers=headers)
    assert response.status_code == 404
    assert response.json()["errorCode"] == "PERF_NOT_FOUND"


def test_add_favorite_twice_returns_409(client, db_session):
    headers = _signup_and_login(client, "favorite-dup@test.com")
    performance_id = _create_performance(db_session, "테스트 공연 B")

    first = client.post(f"/api/v1/users/me/favorites/{performance_id}", headers=headers)
    assert first.status_code == 201

    second = client.post(f"/api/v1/users/me/favorites/{performance_id}", headers=headers)
    assert second.status_code == 409
    assert second.json()["errorCode"] == "MEMBER_FAVORITE_ALREADY_EXISTS"


def test_remove_favorite_not_registered_returns_404(client, db_session):
    headers = _signup_and_login(client, "favorite-remove-missing@test.com")
    performance_id = _create_performance(db_session, "테스트 공연 C")

    response = client.request(
        "DELETE", f"/api/v1/users/me/favorites/{performance_id}", headers=headers
    )
    assert response.status_code == 404
    assert response.json()["errorCode"] == "MEMBER_FAVORITE_NOT_FOUND"


def test_remove_favorite_then_disappears_from_list(client, db_session):
    headers = _signup_and_login(client, "favorite-remove@test.com")
    performance_id = _create_performance(db_session, "테스트 공연 D")

    client.post(f"/api/v1/users/me/favorites/{performance_id}", headers=headers)

    remove_response = client.request(
        "DELETE", f"/api/v1/users/me/favorites/{performance_id}", headers=headers
    )
    assert remove_response.status_code == 200
    assert remove_response.json()["favorited"] is False

    list_response = client.get("/api/v1/users/me/favorites", headers=headers)
    assert list_response.json()["totalElements"] == 0


def test_favorite_list_includes_thumbnail_from_first_image(client, db_session):
    headers = _signup_and_login(client, "favorite-thumbnail@test.com")
    performance_id = _create_performance(db_session, "테스트 공연 E")

    db_session.add_all(
        [
            PerformanceImage(
                performance_id=performance_id, file_key="second.jpg", sort_order=2
            ),
            PerformanceImage(
                performance_id=performance_id, file_key="first.jpg", sort_order=1
            ),
        ]
    )
    db_session.commit()

    client.post(f"/api/v1/users/me/favorites/{performance_id}", headers=headers)

    list_response = client.get("/api/v1/users/me/favorites", headers=headers)
    assert list_response.status_code == 200
    thumbnail_url = list_response.json()["content"][0]["thumbnailUrl"]
    assert thumbnail_url == "first.jpg"  # sort_order가 가장 낮은 이미지
