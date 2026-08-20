"""
[모듈] api/tests/test_performance_image_url.py
[담당] A (B 승인 하에 수정 — 2026-08-20)
[역할] build_image_url()이 참조하던 storage_base_url 설정이 Settings에 선언 안 돼
       있어서 이미지가 있는 공연을 조회하면 AttributeError가 나던 버그의 회귀 테스트.

[구현할 것]
- test_list_performances_with_image_does_not_crash_and_returns_file_key_when_base_url_empty
- test_list_performances_prefixes_file_key_when_base_url_set

[의존]
- tests.conftest (client, db_session 픽스처)

[호출자]
- pytest
"""

from app.core.config import get_settings
from app.domains.performance.model import Category, Performance, PerformanceImage
from app.domains.venue.model import Venue


def _create_performance_with_image(db_session, *, title: str) -> int:
    category = Category(name=f"cat-{title}", sort_order=0)
    venue = Venue(name=f"venue-{title}")
    db_session.add_all([category, venue])
    db_session.flush()

    performance = Performance(
        title=title, category_id=category.id, venue_id=venue.id, status="ACTIVE"
    )
    db_session.add(performance)
    db_session.flush()

    db_session.add(
        PerformanceImage(performance_id=performance.id, file_key="posters/img1.jpg", sort_order=0)
    )
    db_session.commit()
    return performance.id


def test_list_performances_with_image_does_not_crash_and_returns_file_key_when_base_url_empty(
    client, db_session, monkeypatch
):
    monkeypatch.setattr(get_settings(), "storage_base_url", "")
    performance_id = _create_performance_with_image(db_session, title="image-url-empty-base")

    response = client.get("/api/v1/performances")

    assert response.status_code == 200
    item = next(p for p in response.json()["content"] if p["id"] == performance_id)
    assert item["thumbnailUrl"] == "posters/img1.jpg"


def test_list_performances_prefixes_file_key_when_base_url_set(client, db_session, monkeypatch):
    monkeypatch.setattr(get_settings(), "storage_base_url", "https://cdn.example.com/")
    performance_id = _create_performance_with_image(db_session, title="image-url-with-base")

    response = client.get("/api/v1/performances")

    item = next(p for p in response.json()["content"] if p["id"] == performance_id)
    assert item["thumbnailUrl"] == "https://cdn.example.com/posters/img1.jpg"
