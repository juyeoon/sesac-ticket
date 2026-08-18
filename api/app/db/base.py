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
- api/scripts/sql/sesac_ticket_init.sql(스키마 원본, B와 공유됨)이 전 테이블 PK/FK를
  bigint로 정의하므로, Mapped[int]가 기본으로 BIGINT를 쓰도록 type_annotation_map에
  등록해둔다. 이 파일을 상속하는 한 A/B 모두 별도 설정 없이 bigint와 일치한다.
- SQLite는 BIGINT PRIMARY KEY를 rowid-autoincrement로 인식하지 않아 PK가 채워지지
  않는 문제가 있다(로컬 스모크 테스트에서 실제로 발견됨). MySQL/Postgres에서는
  BIGINT AUTO_INCREMENT가 정상 동작하므로, with_variant로 SQLite에서만 INTEGER로
  낮춰서 로컬 sqlite 테스트도 정상 동작하게 한다.
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    type_annotation_map = {
        int: BigInteger().with_variant(Integer, "sqlite"),
    }


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
