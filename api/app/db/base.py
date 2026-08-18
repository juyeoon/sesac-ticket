"""
[모듈] api/app/db/base.py
[담당] 공통
[역할] SQLAlchemy DeclarativeBase 및 공통 Mixin 정의.

[구현할 것]
- class Base(DeclarativeBase)
- class TimestampMixin: created_at (전 테이블 공통)

[의존]
- 없음

[호출자]
- 전 도메인 model.py (A: member/admin, B: venue/performance/reservation/payment)
- app.db.registry (Base.metadata를 Alembic에 노출)

[주의]
- 모든 도메인 model이 이 Base를 상속해야 app.db.registry에서 일관되게 인식되고
  Alembic이 테이블을 자동 감지할 수 있음.
- updated_at은 모든 테이블에 있는 컬럼이 아니므로(sesac ticket.sql 기준) 믹스인에
  넣지 않는다. 필요한 도메인(performance 등)은 모델에서 직접 추가할 것.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
