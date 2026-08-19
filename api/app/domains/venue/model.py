"""
[모듈] api/app/domains/venue/model.py
[담당] B
[역할] 공연장(venue)과 물리적 좌석(venue_seat) 테이블 매핑.

[구현할 것]
- class Venue(Base)
    id, name, address 컬럼. created_at/updated_at 없음(ERD 기준).
- class VenueSeat(Base)
    id, venue_id, section, row_no, seat_no, x, y, grade 컬럼.
    x/y는 좌석 배치도 렌더링용 좌표(픽셀 또는 임의 단위 좌표계).
    created_at/updated_at 없음(ERD 기준).

[의존]
- app.db.base (Base)

[호출자]
- app.domains.venue.repository
- app.db.registry (Base.metadata를 Alembic에 노출하기 위해 import)

[주의]
- venue_seat는 공연장에 고정된 물리적 좌석 정보만 담는다. 회차별 판매 상태
  (AVAILABLE/HELD/RESERVED — SOLD는 없음)는 여기 두지 않고 reservation
  도메인의 schedule_seat에서 별도로 관리한다. 하나의 물리 좌석이 여러
  회차에서 서로 다른 상태를 가질 수 있기 때문.
- grade(좌석 등급)는 여기서는 물리적 구획일 뿐이고, 실제 가격은
  performance.performance_seat_grade에서 공연별로 정의한다.

[TODO] 없음 (구현 완료)
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Venue(Base):
    __tablename__ = "venue"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    address: Mapped[str | None]


class VenueSeat(Base):
    __tablename__ = "venue_seat"

    id: Mapped[int] = mapped_column(primary_key=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venue.id"))
    section: Mapped[str]
    row_no: Mapped[str]
    seat_no: Mapped[int]
    x: Mapped[int | None]
    y: Mapped[int | None]
    grade: Mapped[str]
