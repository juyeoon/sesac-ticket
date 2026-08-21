"""
[모듈] api/app/domains/reservation/model.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 회차별 좌석 상태, 좌석 선점 로그, 예매, 예매-좌석 매핑 테이블 매핑.

[구현할 것]
- class ScheduleSeat(Base)
    id, schedule_id(FK), venue_seat_id(FK), grade, price, status
- class SeatHoldLog(Base)
    id, hold_id(unique), member_id(FK), schedule_id(FK), schedule_seat_ids(JSON),
    status, expires_at, released_at, created_at
- class Reservation(Base)
    id, member_id(FK), schedule_id(FK), hold_id(unique FK->seat_hold_log.hold_id),
    payment_method, status, total_amount, created_at, confirmed_at, cancelled_at
- class ReservationSeat(Base)
    id, reservation_id(FK), schedule_seat_id(FK), price_snapshot

[의존]
- app.db.base (Base)
- app.domains.performance.model (Schedule) — FK 참조용
- app.domains.venue.model (VenueSeat) — FK 참조용
- app.domains.member.model (Member) — FK 참조용

[호출자]
- app.domains.reservation.repository, hold_service, service

[주의]
- reservation 도메인은 통째로 writer(get_db)만 사용한다 (분담표 원칙 — reader는
  read_only라 SELECT FOR UPDATE가 즉시 에러).
- 좌석 상태의 진실은 Valkey master. ScheduleSeat.status는 확정 기록용 보조 데이터.
- api/scripts/sql/sesac_ticket_init.sql이 스키마 정본이며, 컬럼 정의는 그 파일과
  반드시 일치시킨다.
"""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ScheduleSeat(Base):
    __tablename__ = "schedule_seat"

    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedule.id"), nullable=False)
    venue_seat_id: Mapped[int] = mapped_column(ForeignKey("venue_seat.id"), nullable=False)
    grade: Mapped[str]
    price: Mapped[int]
    status: Mapped[str]  # AVAILABLE, HELD, PENDING_PAYMENT, RESERVED


class SeatHoldLog(Base):
    __tablename__ = "seat_hold_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    hold_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"), nullable=False)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedule.id"), nullable=False)
    schedule_seat_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    status: Mapped[str]  # HOLDING, RELEASED, EXPIRED, CONVERTED
    expires_at: Mapped[datetime]
    released_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Reservation(Base):
    __tablename__ = "reservation"

    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"), nullable=False)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedule.id"), nullable=False)
    hold_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("seat_hold_log.hold_id"), unique=True, nullable=False
    )
    payment_method: Mapped[str]  # BANK_TRANSFER, PG
    status: Mapped[str]  # PENDING_PAYMENT, CONFIRMED, CANCELLED, EXPIRED
    total_amount: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    confirmed_at: Mapped[datetime | None] = mapped_column(default=None)
    cancelled_at: Mapped[datetime | None] = mapped_column(default=None)


class ReservationSeat(Base):
    __tablename__ = "reservation_seat"

    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservation.id"), nullable=False)
    schedule_seat_id: Mapped[int] = mapped_column(
        ForeignKey("schedule_seat.id"), nullable=False
    )
    price_snapshot: Mapped[int]
