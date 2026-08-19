"""
[모듈] api/app/domains/reservation/router.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 좌석 상태/선점/해제 + 무통장입금 예매 생성/확정/조회 + 내 예매 목록 라우팅.
       api 설계서 RESV-002~007, 012, 013 대응.

[구현할 것]
- GET    /schedules/{scheduleId}/seats                          RESV-002 (읽기 전용 → get_read_db)
- POST   /seats/hold                                             RESV-003 (writer)
- DELETE /seats/hold/{holdId}                                    RESV-012 (writer)
- GET    /seats/hold/{holdId}                                    RESV-013 (Valkey만 사용, DB 세션 불필요)
- POST   /reservations/bank-transfer                             RESV-004 (writer)
- POST   /reservations/bank-transfer/{reservationId}/confirm     RESV-005 (관리자 전용, writer)
- GET    /reservations/bank-transfer/{reservationId}             RESV-006 (writer, 본인 확인)
- GET    /users/me/reservations                                  RESV-007 (writer — 복제 지연 회피)

[의존]
- app.deps.auth (get_current_member, get_current_admin)
- app.db.routing (get_db, get_read_db)
- app.domains.reservation.service, hold_service

[호출자]
- app.api.v1

[주의]
- entryTicket은 설계서 규격대로 헤더가 아니라 HoldRequest 바디에 실려 온다 —
  hold_service.create_hold 내부에서 verify_entry_ticket_value로 검증한다.
- 이 라우터는 공통 prefix가 없다 — 경로가 /schedules, /seats, /reservations,
  /users/me 로 제각각이라 각 엔드포인트가 전체 경로를 직접 명시한다.
- RESV-001(회차 목록 응답 형식)은 B 담당 domains/performance/router.py에 있고
  아직 설계서와 불일치가 남아있다 (.mypc/예매-도메인-구현계획.md 3-1 참고,
  B에게 이미 공유됨) — 이 라우터의 책임 범위 밖이라 여기서는 건드리지 않는다.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.routing import get_db, get_read_db
from app.deps.auth import get_current_admin, get_current_member
from app.domains.admin.model import Admin
from app.domains.member.model import Member
from app.domains.reservation import hold_service, service
from app.domains.reservation.schema import (
    ConfirmReservationResponse,
    CreateReservationRequest,
    CreateReservationResponse,
    HoldDetailResponse,
    HoldRequest,
    HoldResponse,
    MyReservationListResponse,
    ReleaseHoldResponse,
    ReservationDetailResponse,
    SeatStatusItem,
)

router = APIRouter(tags=["reservation"])


@router.get("/schedules/{schedule_id}/seats", response_model=list[SeatStatusItem])
def get_seat_status(
    schedule_id: int,
    db: Session = Depends(get_read_db),
    member: Member = Depends(get_current_member),
) -> list[SeatStatusItem]:
    return service.get_seat_status_list(db, schedule_id)


@router.post("/seats/hold", response_model=HoldResponse)
def create_hold(
    request: HoldRequest,
    db: Session = Depends(get_db),
    member: Member = Depends(get_current_member),
) -> HoldResponse:
    result = hold_service.create_hold(
        db,
        member_id=member.id,
        schedule_id=request.schedule_id,
        seat_ids=request.seat_ids,
        entry_ticket=request.entry_ticket,
    )
    return HoldResponse(
        hold_id=result.hold_id, seat_ids=result.seat_ids, expires_at=result.expires_at
    )


@router.delete("/seats/hold/{hold_id}", response_model=ReleaseHoldResponse)
def release_hold(
    hold_id: str,
    db: Session = Depends(get_db),
    member: Member = Depends(get_current_member),
) -> ReleaseHoldResponse:
    hold_service.release_hold(db, hold_id=hold_id, member_id=member.id)
    return ReleaseHoldResponse(hold_id=hold_id, released=True)


@router.get("/seats/hold/{hold_id}", response_model=HoldDetailResponse)
def get_hold(
    hold_id: str,
    member: Member = Depends(get_current_member),
) -> HoldDetailResponse:
    detail = hold_service.get_hold(hold_id=hold_id, member_id=member.id)
    return HoldDetailResponse(
        hold_id=detail.hold_id,
        seat_ids=detail.seat_ids,
        expires_at=detail.expires_at,
        remaining_seconds=detail.remaining_seconds,
    )


@router.post(
    "/reservations/bank-transfer", response_model=CreateReservationResponse, status_code=201
)
def create_reservation(
    request: CreateReservationRequest,
    db: Session = Depends(get_db),
    member: Member = Depends(get_current_member),
) -> CreateReservationResponse:
    return service.create_reservation(
        db, member_id=member.id, hold_id=request.hold_id, depositor_name=request.depositor_name
    )


@router.post(
    "/reservations/bank-transfer/{reservation_id}/confirm",
    response_model=ConfirmReservationResponse,
)
def confirm_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
) -> ConfirmReservationResponse:
    return service.confirm_reservation(db, reservation_id=reservation_id, admin_id=admin.id)


@router.get(
    "/reservations/bank-transfer/{reservation_id}", response_model=ReservationDetailResponse
)
def get_reservation_detail(
    reservation_id: int,
    db: Session = Depends(get_db),
    member: Member = Depends(get_current_member),
) -> ReservationDetailResponse:
    return service.get_reservation_detail(
        db, reservation_id=reservation_id, member_id=member.id
    )


@router.get("/users/me/reservations", response_model=MyReservationListResponse)
def list_my_reservations(
    page: int = Query(default=0, ge=0),
    size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    member: Member = Depends(get_current_member),
) -> MyReservationListResponse:
    return service.list_my_reservations(
        db, member_id=member.id, page=page, size=size, status=status
    )
