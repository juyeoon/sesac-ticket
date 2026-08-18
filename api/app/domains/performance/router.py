from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.routing import get_read_db
from app.domains.performance import service
from app.domains.performance.schema import (
    PerformanceDetailResponse,
    PerformanceListEnvelope,
    ScheduleResponse,
)

router = APIRouter(prefix="/performances", tags=["performance"])


@router.get(
    "",
    response_model=PerformanceListEnvelope,
    summary="공연 목록 조회",
    description="전체 공연을 status 구분 없이 조회한다(ACTIVE/HIDDEN/ENDED 전부). 필터링은 프런트에서.",
)
def list_performances(db: Session = Depends(get_read_db)):
    return service.get_performance_list(db)


@router.get(
    "/search",
    response_model=PerformanceListEnvelope,
    summary="공연 검색",
    description="제목에 검색어(keyword)가 포함된 공연을 부분 일치로 조회한다. status 구분 없음, 페이징 없음.",
)
def search_performances(
    keyword: str = Query(min_length=1, description="검색어(제목 부분 일치)"),
    db: Session = Depends(get_read_db),
):
    return service.search_performances(db, keyword)


@router.get(
    "/{performance_id}",
    response_model=PerformanceDetailResponse,
    summary="공연 상세 조회",
    description="공연 이름/카테고리/설명/티켓구매기간/가격/관람시간/관람등급/좌석등급/위치/이미지를 반환한다.",
)
def get_performance_detail(
    performance_id: int,
    db: Session = Depends(get_read_db),
):
    return service.get_performance_detail(db, performance_id)


@router.get(
    "/{performance_id}/schedules",
    response_model=list[ScheduleResponse],
    summary="회차 목록 조회",
    description="공연의 전체 회차와 회차별 판매 상태(ON_SALE/SOLD_OUT/CLOSED)를 반환한다.",
)
def get_performance_schedules(
    performance_id: int,
    db: Session = Depends(get_read_db),
):
    return service.get_schedules(db, performance_id)
