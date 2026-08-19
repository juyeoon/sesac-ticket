"""
[모듈] api/tests/test_support.py
[담당] A
[역할] 고객센터 게시글 목록/상세 조회 테스트 (API-ETC-001, 002).

[구현할 것]
- test_list_support_posts_empty_when_no_posts
- test_list_support_posts_returns_multiple_posts
- test_list_support_posts_paginates
- test_list_support_posts_filters_by_category
- test_list_support_posts_requires_no_auth
- test_get_support_post_detail_success
- test_get_support_post_detail_requires_no_auth
- test_get_support_post_detail_returns_404_for_missing_post

[의존]
- tests.conftest (client, db_session 픽스처)
- app.domains.support.model

[호출자]
- pytest
"""

from app.domains.support.model import SupportPost


def _create_post(db_session, *, title: str, category: str | None = "notice") -> int:
    post = SupportPost(title=title, content=f"{title}-content", category=category)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post.id


def test_list_support_posts_empty_when_no_posts(client):
    response = client.get("/api/v1/support/posts", params={"category": "no-such-category-xyz"})
    assert response.status_code == 200
    body = response.json()
    assert body["totalElements"] == 0
    assert body["content"] == []


def test_list_support_posts_returns_multiple_posts(client, db_session):
    _create_post(db_session, title="list-basic-1", category="list-basic-cat")
    _create_post(db_session, title="list-basic-2", category="list-basic-cat")

    response = client.get("/api/v1/support/posts", params={"category": "list-basic-cat"})
    assert response.status_code == 200
    body = response.json()
    assert body["totalElements"] == 2
    assert {item["title"] for item in body["content"]} == {"list-basic-1", "list-basic-2"}
    assert "content" not in body["content"][0]  # 목록 항목은 본문(content)을 포함하지 않는다


def test_list_support_posts_paginates(client, db_session):
    for i in range(3):
        _create_post(db_session, title=f"page-post-{i}", category="page-cat")

    page0 = client.get(
        "/api/v1/support/posts", params={"category": "page-cat", "page": 0, "size": 2}
    ).json()
    page1 = client.get(
        "/api/v1/support/posts", params={"category": "page-cat", "page": 1, "size": 2}
    ).json()

    assert page0["totalElements"] == 3
    assert len(page0["content"]) == 2
    assert len(page1["content"]) == 1


def test_list_support_posts_filters_by_category(client, db_session):
    _create_post(db_session, title="filter-notice", category="filter-notice-cat")
    _create_post(db_session, title="filter-faq", category="filter-faq-cat")

    response = client.get(
        "/api/v1/support/posts", params={"category": "filter-notice-cat"}
    )
    body = response.json()
    assert body["totalElements"] == 1
    assert body["content"][0]["title"] == "filter-notice"


def test_list_support_posts_requires_no_auth(client, db_session):
    _create_post(db_session, title="no-auth-list", category="no-auth-list-cat")

    response = client.get(
        "/api/v1/support/posts", params={"category": "no-auth-list-cat"}
    )
    assert response.status_code == 200


def test_get_support_post_detail_success(client, db_session):
    post_id = _create_post(db_session, title="detail-post", category="detail-cat")

    response = client.get(f"/api/v1/support/posts/{post_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == post_id
    assert body["title"] == "detail-post"
    assert body["content"] == "detail-post-content"
    assert body["category"] == "detail-cat"
    assert "createdAt" in body


def test_get_support_post_detail_requires_no_auth(client, db_session):
    post_id = _create_post(db_session, title="no-auth-detail", category="no-auth-detail-cat")

    response = client.get(f"/api/v1/support/posts/{post_id}")
    assert response.status_code == 200


def test_get_support_post_detail_returns_404_for_missing_post(client):
    response = client.get("/api/v1/support/posts/999999")
    assert response.status_code == 404
    assert response.json()["errorCode"] == "SUPPORT_POST_NOT_FOUND"
