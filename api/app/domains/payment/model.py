"""
[모듈] api/app/domains/payment/model.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 무통장입금 결제 정보 테이블 매핑. (pg_payment는 이번 범위 밖)

[구현할 것]
- class BankTransferPayment(Base)
    id, reservation_id(unique FK), depositor_name, bank_account_info,
    payment_due_at, confirmed_by_admin_id(nullable FK), confirmed_at

[의존]
- app.db.base (Base)
- app.domains.reservation.model (Reservation) — FK 참조용
- app.domains.admin.model (Admin) — FK 참조용

[호출자]
- app.domains.reservation.service (예매 생성 시 입금 정보 동시 생성)

[주의]
- PG 결제(pg_payment)는 이번 범위에서 제외 (무통장입금만 지원).
"""

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BankTransferPayment(Base):
    __tablename__ = "bank_transfer_payment"

    id: Mapped[int] = mapped_column(primary_key=True)
    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservation.id"), unique=True, nullable=False
    )
    depositor_name: Mapped[str]
    bank_account_info: Mapped[str]
    payment_due_at: Mapped[datetime]
    confirmed_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin.id"), default=None
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(default=None)
