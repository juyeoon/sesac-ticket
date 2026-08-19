"""
[모듈] api/app/domains/support/router.py
[담당] A
[역할] 고객센터 게시글 목록/상세 조회 라우팅. api 설계서 API-ETC-001, 002 대응.

[구현할 것]
- GET /support/posts            API-ETC-001 (인증 불필요, get_read_db)
- GET /support/posts/{post_id}  API-ETC-002 (인증 불필요, get_read_db)

[의존]
- app.domains.support.service
- app.db.routing (get_read_db)

[호출자]
- app.api.v1
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.routing import get_read_db
from app.domains.support import service
from app.domains.support.schema import SupportPostDetailResponse, SupportPostListResponse

router = APIRouter(prefix="/support", tags=["support"])


@router.get("/posts", response_model=SupportPostListResponse)
def list_support_posts(
    page: int = Query(default=0, ge=0),
    size: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None),
    db: Session = Depends(get_read_db),
) -> SupportPostListResponse:
    return service.list_support_posts(db, page=page, size=size, category=category)


@router.get("/posts/{post_id}", response_model=SupportPostDetailResponse)
def get_support_post_detail(
    post_id: int,
    db: Session = Depends(get_read_db),
) -> SupportPostDetailResponse:
    return service.get_support_post_detail(db, post_id)
