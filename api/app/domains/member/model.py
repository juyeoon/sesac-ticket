"""
[모듈] api/app/domains/member/model.py
[담당] A
[역할] member 테이블 매핑. (member_favorite은 이번 범위 밖)

[구현할 것]
- class Member(Base, TimestampMixin)
    id, email, password_hash, nickname, gender, age_range, status,
    email_verified, withdrawn_at, created_at

[의존]
- app.db.base (Base, TimestampMixin)

[호출자]
- app.domains.member.repository
- app.domains.auth.service, app.deps.auth

[주의]
- password_hash는 schema(DTO)에 절대 노출하지 않는다.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

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
