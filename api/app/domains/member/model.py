"""
[모듈] api/app/domains/member/model.py
[담당] A
[역할] member 테이블 및 member_favorite(관심 공연) 테이블 매핑.

[구현할 것]
- class Member(Base, TimestampMixin)
    id, email, password_hash, nickname, gender, age_range, status,
    email_verified, withdrawn_at, created_at
- class MemberFavorite(Base)
    id, member_id, performance_id, created_at

[의존]
- app.db.base (Base, TimestampMixin)
- app.domains.performance.model (Performance) — FK 참조용

[호출자]
- app.domains.member.repository, app.domains.member.favorite_repository
- app.domains.auth.service, app.deps.auth

[주의]
- password_hash는 schema(DTO)에 절대 노출하지 않는다.
- MemberFavorite은 B의 performance 테이블을 FK로 참조한다. B가 domains/performance
  모델을 만들어 놓은 뒤부터 이 파일도 함께 동작한다 (그 전엔 raw SQL로 대체 구현했었음).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


class Member(Base, TimestampMixin):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(255), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(255))
    age_range: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(255), nullable=False, default="ACTIVE")
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime)


class MemberFavorite(Base):
    __tablename__ = "member_favorite"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"), nullable=False)
    performance_id: Mapped[int] = mapped_column(ForeignKey("performance.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
