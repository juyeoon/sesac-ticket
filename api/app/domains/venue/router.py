"""
[모듈] api/app/domains/venue/router.py
[담당] B
[역할] 공연장 좌석 배치도 조회 엔드포인트. (API-PERF-005)

[구현할 것]
- GET /venues/{venue_id}/seat-map -> VenueSeatMapResponse
    공연장의 좌석 배치도를 구역(section)별로 묶어서 반환한다. 회차와 무관하게
    물리적 배치만 조회한다. scheduleId 쿼리 파라미터는 받지만(api명세서.xlsx
    스펙에 있음) 응답에 영향을 주지 않는다 — 아래 [주의] 참고.

[의존]
- app.domains.venue.repository
- app.db.routing (get_read_db)

[호출자]
- app.api.v1 (B 구역에 include_router)

[주의]
- 전부 읽기 전용. get_read_db(reader)만 사용한다.
- 여기서 반환하는 좌석 정보는 물리적 좌표/구역/등급뿐이다. 좌석의 실시간
  판매 상태(AVAILABLE/HELD/RESERVED — SOLD는 없음)나 가격이 필요한 화면
  (예매 페이지)은 RESV-002(회차 기준 좌석 상태 조회)를 따로 써야 한다.
- venue_id가 없으면 PERF_VENUE_NOT_FOUND(404).
- schedule_id는 스펙상 "회차별 등급/가격 매핑 시" 쓴다고 돼 있지만, 실제
  좌석 등급(venue_seat.grade)은 회차와 무관하게 고정값이고 가격 자체가
  이 응답에 없다. api명세서.xlsx 비고에도 "좌표 데이터는 정적이라 캐시 대상,
  실시간 상태는 RESV-002와 프런트에서 병합"이라고 돼 있어서, 이 API는
  일부러 정적으로 유지하고 schedule_id는 받기만 하고 로직에서 쓰지 않는다.
  나중에 스펙이 바뀌면(예: 회차별 매진 여부까지 여기서 내려줘야 한다면)
  그때 반영한다.

[TODO] 없음 (구현 완료)
"""

from itertools import groupby

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import AppException, ErrorCode
from app.db.routing import get_read_db
from app.domains.venue import repository
from app.domains.venue.schema import SeatCoordinate, SeatMapSection, VenueSeatMapResponse

router = APIRouter(prefix="/venues", tags=["venue"])


@router.get(
    "/{venue_id}/seat-map",
    response_model=VenueSeatMapResponse,
    summary="공연장 좌석 배치도 조회",
    description="공연장의 좌석 배치도를 구역별로 묶어서 조회한다. 실시간 판매 상태/가격은 포함하지 않는다.",
)
def get_venue_seat_map(
    venue_id: int,
    schedule_id: int | None = Query(
        default=None,
        alias="scheduleId",
        description="회차 ID(선택). 현재는 응답에 영향을 주지 않음 — 좌표는 회차 무관 정적 데이터.",
    ),
    db: Session = Depends(get_read_db),
):
    venue = repository.get_venue(db, venue_id)
    if venue is None:
        raise AppException(ErrorCode.PERF_VENUE_NOT_FOUND)

    seats = repository.get_seats_by_venue(db, venue_id)
    sections = [
        SeatMapSection(
            section_name=section_name,
            seats=[
                SeatCoordinate(
                    seat_id=s.id,
                    row=s.row_no,
                    number=s.seat_no,
                    x=s.x,
                    y=s.y,
                    grade=s.grade,
                )
                for s in group
            ],
        )
        for section_name, group in groupby(seats, key=lambda s: s.section)
    ]
    return VenueSeatMapResponse(venue_id=venue_id, sections=sections)
