"""
[모듈] api/app/domains/reservation/schema.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 예매 도메인 요청/응답 DTO. api 설계서 규격(camelCase)을 따른다.

[구현할 것]
- SeatStatusItem ({ seatId, section, row, number, grade, status }) — RESV-002
- HoldRequest ({ scheduleId, seatIds, entryTicket }) — RESV-003 요청
- HoldResponse ({ holdId, seatIds, expiresAt }) — RESV-003 응답
- ReleaseHoldResponse ({ holdId, released }) — RESV-012 응답
- HoldDetailResponse ({ holdId, seatIds, expiresAt, remainingSeconds }) — RESV-013 응답
- CreateReservationRequest ({ holdId, depositorName }) — RESV-004 요청
- CreateReservationResponse ({ reservationId, status, paymentMethod, bankAccountInfo, paymentDueAt }) — RESV-004 응답
- ConfirmReservationResponse ({ reservationId, status, confirmedAt }) — RESV-005 응답
- ReservationSeatItem ({ section, row, number, grade, price }) — RESV-006 seats 항목
- ReservationPerformanceSummary ({ performanceId, title })
- ReservationScheduleSummary ({ scheduleId, date, time })
- ReservationDetailResponse — RESV-006 응답
- MyReservationItem / MyReservationListResponse ({ content, totalElements }) — RESV-007
- AdminReservationMember ({ memberId, nickname, email })
- AdminReservationListItem — GET /reservations/list(관리자 전용) 응답 항목.
    performance/schedule/seats는 기존 ReservationPerformanceSummary/
    ReservationScheduleSummary/ReservationSeatItem을 그대로 재사용.

[의존]
- pydantic

[호출자]
- app.domains.reservation.service, router
"""

from datetime import date as date_, datetime, time as time_, timezone
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict
from pydantic.alias_generators import to_camel


def _assume_utc(value: object) -> object:
    """MySQL DATETIME 컬럼은 tzinfo를 안 보존해서 왕복하면 naive datetime으로 돌아온다.
    저장 시점에 항상 UTC로 넣도록 통일했으므로(service.py/hold_service.py 등), naive로
    돌아온 값은 UTC로 간주해 명시적으로 오프셋을 붙인다 — 그래야 응답 JSON에 오프셋이
    포함되고, 프론트가 서버/브라우저 시간대에 관계없이 정확히 변환할 수 있다."""
    if isinstance(value, datetime) and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


UtcDateTime = Annotated[datetime, BeforeValidator(_assume_utc)]


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SeatStatusItem(_CamelModel):
    seat_id: int
    section: str
    row: str
    number: int
    grade: str
    status: str


class HoldRequest(_CamelModel):
    schedule_id: int
    seat_ids: list[int]
    entry_ticket: str | None = None


class HoldResponse(_CamelModel):
    hold_id: str
    seat_ids: list[int]
    expires_at: UtcDateTime


class ReleaseHoldResponse(_CamelModel):
    hold_id: str
    released: bool = True


class HoldDetailResponse(_CamelModel):
    hold_id: str
    seat_ids: list[int]
    expires_at: UtcDateTime
    remaining_seconds: int


class CreateReservationRequest(_CamelModel):
    hold_id: str
    depositor_name: str


class CreateReservationResponse(_CamelModel):
    reservation_id: int
    status: str
    payment_method: str
    bank_account_info: str
    payment_due_at: UtcDateTime


class ConfirmReservationResponse(_CamelModel):
    reservation_id: int
    status: str
    confirmed_at: UtcDateTime


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
    payment_due_at: UtcDateTime | None
    confirmed_at: UtcDateTime | None


class MyReservationItem(_CamelModel):
    reservation_id: int
    performance_title: str
    date: date_
    status: str
    confirmed_at: UtcDateTime | None


class MyReservationListResponse(_CamelModel):
    content: list[MyReservationItem]
    total_elements: int


class AdminReservationMember(_CamelModel):
    member_id: int
    nickname: str
    email: str


class AdminReservationListItem(_CamelModel):
    reservation_id: int
    status: str
    confirmed_at: UtcDateTime | None
    depositor_name: str | None
    member: AdminReservationMember
    performance: ReservationPerformanceSummary
    schedule: ReservationScheduleSummary
    seats: list[ReservationSeatItem]
