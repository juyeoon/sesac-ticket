"""
[모듈] api/app/domains/reservation/schema.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 예매 도메인 요청/응답 DTO. api 설계서 규격(camelCase)을 따른다.

[구현할 것]
- SeatStatusItem ({ seatId, section, row, number, grade, status }) — RESV-002
- CreateReservationRequest ({ holdId, depositorName }) — RESV-004 요청
- CreateReservationResponse ({ reservationId, status, paymentMethod, bankAccountInfo, paymentDueAt }) — RESV-004 응답
- ConfirmReservationResponse ({ reservationId, status, confirmedAt }) — RESV-005 응답
- ReservationSeatItem ({ section, row, number, grade, price }) — RESV-006 seats 항목
- ReservationPerformanceSummary ({ performanceId, title })
- ReservationScheduleSummary ({ scheduleId, date, time })
- ReservationDetailResponse — RESV-006 응답

[의존]
- pydantic

[호출자]
- app.domains.reservation.service, router
"""

from datetime import date as date_, datetime, time as time_

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SeatStatusItem(_CamelModel):
    seat_id: int
    section: str
    row: str
    number: int
    grade: str
    status: str


class CreateReservationRequest(_CamelModel):
    hold_id: str
    depositor_name: str


class CreateReservationResponse(_CamelModel):
    reservation_id: int
    status: str
    payment_method: str
    bank_account_info: str
    payment_due_at: datetime


class ConfirmReservationResponse(_CamelModel):
    reservation_id: int
    status: str
    confirmed_at: datetime


class ReservationSeatItem(_CamelModel):
    section: str
    row: str
    number: int
    grade: str
    price: int


class ReservationPerformanceSummary(_CamelModel):
    performance_id: int
    title: str


class ReservationScheduleSummary(_CamelModel):
    schedule_id: int
    date: date_
    time: time_


class ReservationDetailResponse(_CamelModel):
    reservation_id: int
    performance: ReservationPerformanceSummary
    schedule: ReservationScheduleSummary
    seats: list[ReservationSeatItem]
    status: str
    payment_method: str
    bank_account_info: str
    payment_due_at: datetime | None
    confirmed_at: datetime | None
