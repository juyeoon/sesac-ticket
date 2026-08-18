"""
[모듈] api/app/db/base.py
[담당] 공통
[역할] SQLAlchemy DeclarativeBase 및 공통 Mixin 정의.

[구현할 것]
- class Base(DeclarativeBase)
    전 도메인 model이 상속하는 베이스 클래스.
- class TimestampMixin
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime | None]

[의존]
- 없음

[호출자]
- 전 도메인 model.py (A: member/admin, B: venue/performance/reservation/payment)
- app.db.registry (Base.metadata를 Alembic에 노출)

[주의]
- 모든 도메인 model이 이 Base를 상속해야 app.db.registry에서 일관되게 인식되고
  Alembic이 테이블을 자동 감지할 수 있음.

[TODO] 구현 필요
"""

class Base:
    pass


class TimestampMixin:
    pass
