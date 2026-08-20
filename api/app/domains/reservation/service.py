"""
[모듈] api/app/domains/reservation/service.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 좌석 상태 조회(RESV-002) + 무통장입금 예매 생성/확정/조회(RESV-004~006)
       + 내 예매 목록(RESV-007).

[구현할 것]
- get_seat_status_list(db, schedule_id) -> list[SeatStatusItem]
- invalidate_seat_status_cache(schedule_id) -> None
    Hold 생성/해제 시 캐시를 무효화해 다음 조회에서 최신 상태로 재구성되게 한다.
- create_reservation(db, *, member_id, hold_id, depositor_name) -> CreateReservationResponse
- confirm_reservation(db, *, reservation_id, admin_id) -> ConfirmReservationResponse
- expire_reservation(db, reservation) -> None
    reservation_sweeper 전용. 입금기한(payment_due_at)이 지난 PENDING_PAYMENT 예매를
    EXPIRED로 전환 + 좌석 AVAILABLE 복구 + 좌석상태 캐시 무효화.
- get_reservation_detail(db, *, reservation_id, member_id) -> ReservationDetailResponse
- list_my_reservations(db, *, member_id, status=None) -> MyReservationListResponse
    반드시 writer 세션으로 호출 (복제 지연 문제 방지, 분담표 원칙). 페이지네이션 없음.

[의존]
- app.cache.client (get_master_client)
- app.cache.keys (seat_status)
- app.core.config (SEAT_STATUS_CACHE_TTL_SEC, BANK_TRANSFER_PAYMENT_DUE_HOURS, BANK_ACCOUNT_INFO)
- app.domains.reservation.repository

[호출자]
- app.domains.reservation.router (RESV-002, 004, 005, 006)
- app.domains.reservation.hold_service (Hold 생성/해제 후 캐시 무효화)

[주의]
- 밸키 키 설계서 규격대로 `seat:status:{scheduleId}`를 **Hash**로 사용한다
  (field=schedule_seat_id, value=status 문자열만 — section/row/grade 등 정적
  정보는 캐시하지 않고 매번 DB JOIN으로 가져온다. 좌석 배치 자체는 거의 안
  바뀌지만 상태는 자주 바뀌기 때문).
- 캐시가 비어있으면(HLEN==0) DB에서 전체를 읽어 Hash를 채우고 TTL을 건다.
  캐시가 있으면 DB에서 읽은 정적 정보에 캐시된 상태값을 덮어써서 반환한다.
- 엄격한 실시간 정합성이 필요한 곳(선점 시도 자체)은 이 캐시를 쓰지 않고
  hold_service가 DB(schedule_seat.status)와 Lua 락을 직접 확인한다. 이 캐시는
  "좌석 배치도를 보여주는 조회"의 부하를 줄이기 위한 것으로, 최대
  SEAT_STATUS_CACHE_TTL_SEC(기본 5초)만큼 stale할 수 있다.
- create_reservation은 반드시 writer 세션(get_db)으로 호출한다 (분담표 원칙).
  hold_log.status가 HOLDING이 아니면(만료/이미해제/이미전환) RESV_HOLD_EXPIRED(410).
  좌석이 실제로는 HELD가 아니면(스위퍼가 먼저 되돌린 경우 등, 방어적 체크)
  RESV_SEAT_ALREADY_RESERVED(409) — Lua 락과 별개로 DB 레벨에서 한 번 더 확인.
"""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.cache.client import get_master_client
from app.cache.keys import seat_status as seat_status_key
from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.domains.reservation import repository
from app.domains.reservation.model import Reservation
from app.domains.reservation.schema import (
    ConfirmReservationResponse,
    CreateReservationResponse,
    MyReservationItem,
    MyReservationListResponse,
    ReservationDetailResponse,
    ReservationPerformanceSummary,
    ReservationScheduleSummary,
    ReservationSeatItem,
    SeatStatusItem,
)


def get_seat_status_list(db: Session, schedule_id: int) -> list[SeatStatusItem]:
    if not repository.schedule_exists(db, schedule_id):
        raise AppException(ErrorCode.PERF_SCHEDULE_NOT_FOUND)

    seats = repository.get_schedule_seats_with_seat_info(db, schedule_id)
    if not seats:
        return []

    client = get_master_client()
    key = seat_status_key(schedule_id)
    cached_status = client.hgetall(key)

    if cached_status:
        for seat in seats:
            status = cached_status.get(str(seat["seat_id"]))
            if status is not None:
                seat["status"] = status
    else:
        settings = get_settings()
        mapping = {str(seat["seat_id"]): seat["status"] for seat in seats}
        client.hset(key, mapping=mapping)
        client.expire(key, settings.seat_status_cache_ttl_sec)

    return [SeatStatusItem(**seat) for seat in seats]


def invalidate_seat_status_cache(schedule_id: int) -> None:
    client = get_master_client()
    client.delete(seat_status_key(schedule_id))


def create_reservation(
    db: Session, *, member_id: int, hold_id: str, depositor_name: str
) -> CreateReservationResponse:
    hold_log = repository.get_seat_hold_log(db, hold_id)
    if hold_log is None:
        raise AppException(ErrorCode.RESV_HOLD_NOT_FOUND)
    if hold_log.member_id != member_id:
        raise AppException(ErrorCode.RESV_HOLD_OWNER_MISMATCH)
    if hold_log.status != "HOLDING":
        raise AppException(ErrorCode.RESV_HOLD_EXPIRED)

    seats = repository.get_seats_for_hold(
        db, schedule_id=hold_log.schedule_id, seat_ids=hold_log.schedule_seat_ids
    )
    if len(seats) != len(hold_log.schedule_seat_ids) or any(
        seat.status != "HELD" for seat in seats
    ):
        raise AppException(ErrorCode.RESV_SEAT_ALREADY_RESERVED)

    settings = get_settings()
    payment_due_at = datetime.now() + timedelta(
        hours=settings.bank_transfer_payment_due_hours
    )

    reservation = repository.create_reservation_with_payment(
        db,
        member_id=member_id,
        schedule_id=hold_log.schedule_id,
        hold_id=hold_id,
        seats=seats,
        depositor_name=depositor_name,
        bank_account_info=settings.bank_account_info,
        payment_due_at=payment_due_at,
    )
    repository.mark_seats_reserved(db, hold_log.schedule_seat_ids)
    repository.mark_hold_converted(db, hold_log)
    invalidate_seat_status_cache(hold_log.schedule_id)

    return CreateReservationResponse(
        reservation_id=reservation.id,
        status=reservation.status,
        payment_method=reservation.payment_method,
        bank_account_info=settings.bank_account_info,
        payment_due_at=payment_due_at,
    )


def confirm_reservation(
    db: Session, *, reservation_id: int, admin_id: int
) -> ConfirmReservationResponse:
    reservation = repository.get_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise AppException(ErrorCode.RESV_NOT_FOUND)
    if reservation.status != "PENDING_PAYMENT":
        raise AppException(ErrorCode.RESV_INVALID_STATUS_TRANSITION)

    payment = repository.get_bank_transfer_payment(db, reservation_id)
    confirmed_at = datetime.now()
    reservation.status = "CONFIRMED"
    reservation.confirmed_at = confirmed_at
    if payment is not None:
        payment.confirmed_by_admin_id = admin_id
        payment.confirmed_at = confirmed_at
    db.commit()

    return ConfirmReservationResponse(
        reservation_id=reservation.id,
        status=reservation.status,
        confirmed_at=confirmed_at,
    )


def expire_reservation(db: Session, reservation: Reservation) -> None:
    seat_ids = repository.get_reservation_seat_ids(db, reservation.id)
    repository.mark_seats_available(db, seat_ids)
    repository.mark_reservation_expired(db, reservation)
    invalidate_seat_status_cache(reservation.schedule_id)


def get_reservation_detail(
    db: Session, *, reservation_id: int, member_id: int
) -> ReservationDetailResponse:
    reservation = repository.get_reservation_by_id(db, reservation_id)
    if reservation is None:
        raise AppException(ErrorCode.RESV_NOT_FOUND)
    if reservation.member_id != member_id:
        raise AppException(ErrorCode.RESV_OWNER_MISMATCH)

    schedule = repository.get_schedule_with_performance(db, reservation.schedule_id)
    payment = repository.get_bank_transfer_payment(db, reservation_id)
    seats = repository.get_reservation_seats_detail(db, reservation_id)

    return ReservationDetailResponse(
        reservation_id=reservation.id,
        performance=ReservationPerformanceSummary(
            performance_id=schedule.performance.id, title=schedule.performance.title
        ),
        schedule=ReservationScheduleSummary(
            schedule_id=schedule.id, date=schedule.perf_date, time=schedule.perf_time
        ),
        seats=[ReservationSeatItem(**seat) for seat in seats],
        status=reservation.status,
        payment_method=reservation.payment_method,
        bank_account_info=payment.bank_account_info if payment else "",
        payment_due_at=payment.payment_due_at if payment else None,
        confirmed_at=reservation.confirmed_at,
    )


def list_my_reservations(
    db: Session, *, member_id: int, status: str | None = None
) -> MyReservationListResponse:
    items, total = repository.list_reservations_by_member(db, member_id, status=status)
    return MyReservationListResponse(
        content=[MyReservationItem(**item) for item in items],
        total_elements=total,
    )
