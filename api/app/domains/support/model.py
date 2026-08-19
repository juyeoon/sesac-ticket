"""
[모듈] api/app/domains/support/model.py
[담당] A
[역할] 고객센터 게시글 테이블 매핑. api 설계서 API-ETC-001/002에 대응.

[구현할 것]
- class SupportPost(Base, TimestampMixin)
    id, title, content, category(nullable), created_at, updated_at(nullable)

[의존]
- app.db.base (Base, TimestampMixin)

[호출자]
- app.domains.support.repository

[주의]
- 조회 전용 도메인이다 — 설계서에 작성/수정/삭제 API가 없다(1차 범위: 경로+게시판
  조회만). 게시글 데이터는 seed.py 또는 DB 직접 입력으로 채운다.
- api/scripts/sql/sesac_ticket_init.sql이 스키마 정본이며, 컬럼 정의는 그 파일과
  반드시 일치시킨다.
"""

from datetime import datetime

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SupportPost(Base, TimestampMixin):
    __tablename__ = "support_post"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    content: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None]
    updated_at: Mapped[datetime | None] = mapped_column(default=None)
