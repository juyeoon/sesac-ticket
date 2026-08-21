from datetime import datetime

from sqlalchemy import text

from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.domains.performance import repository
from app.domains.performance.schema import (
    CategorySummary,
    PerformanceDetailResponse,
    PerformanceImageInfo,
    PerformanceListEnvelope,
    PerformanceSummary,
    PriceRange,
    ScheduleDetailResponse,
    ScheduleResponse,
    ScheduleSummary,
    SeatGradeAvailability,
    SeatGradeInfo,
    VenueSummary,
)


def build_image_url(file_key):
    base = get_settings().storage_base_url.rstrip("/")
    return f"{base}/{file_key}" if base else file_key


def calculate_sale_status(schedule, ticket_open_at, ticket_close_at, remaining_seats):
    if schedule.status != "OPEN":
        return "CLOSED"

    now = datetime.now()
    if ticket_open_at and now < ticket_open_at:
        return "CLOSED"
    if ticket_close_at and now > ticket_close_at:
        return "CLOSED"

    return "SOLD_OUT" if remaining_seats <= 0 else "ON_SALE"


def _remaining_seats(db, schedule_id):
    return db.execute(
        text(
            "SELECT COUNT(*) FROM schedule_seat "
            "WHERE schedule_id = :sid AND status = 'AVAILABLE'"
        ),
        {"sid": schedule_id},
    ).scalar()


def _schedule_sale_status(db, schedule, ticket_open_at, ticket_close_at):
    remaining = _remaining_seats(db, schedule.id)
    return calculate_sale_status(schedule, ticket_open_at, ticket_close_at, remaining)


def _seat_grade_availability(db, schedule_id):
    rows = db.execute(
        text(
            "SELECT grade, price, SUM(CASE WHEN status = 'AVAILABLE' THEN 1 ELSE 0 END) AS remaining "
            "FROM schedule_seat WHERE schedule_id = :sid GROUP BY grade, price"
        ),
        {"sid": schedule_id},
    ).all()
    return [
        SeatGradeAvailability(grade=grade, price=price, remaining=remaining)
        for grade, price, remaining in rows
    ]


def _to_schedule_summary(db, schedule):
    return ScheduleSummary(
        schedule_id=schedule.id,
        date=schedule.perf_date,
        time=schedule.perf_time,
        seat_grades=_seat_grade_availability(db, schedule.id),
    )


def _to_summary(performance):
    thumbnail = performance.images[0] if performance.images else None
    schedule_dates = [s.perf_date for s in performance.schedules]
    return PerformanceSummary(
        id=performance.id,
        title=performance.title,
        thumbnail_url=build_image_url(thumbnail.file_key) if thumbnail else None,
        category=CategorySummary(id=performance.category.id, name=performance.category.name),
        venue=VenueSummary(
            id=performance.venue.id,
            name=performance.venue.name,
            address=performance.venue.address,
        ),
        date_from=min(schedule_dates) if schedule_dates else None,
        date_to=max(schedule_dates) if schedule_dates else None,
        ticket_open_at=performance.ticket_open_at,
        ticket_close_at=performance.ticket_close_at,
        status=performance.status,
    )


def get_performance_list(db):
    performances = repository.list_performances(db)
    content = [_to_summary(p) for p in performances]
    return PerformanceListEnvelope(content=content, total_elements=len(content))


def search_performances(db, keyword):
    performances = repository.search_performances(db, keyword)
    content = [_to_summary(p) for p in performances]
    return PerformanceListEnvelope(content=content, total_elements=len(content))


def get_performance_detail(db, performance_id):
    performance = repository.get_performance_detail(db, performance_id)
    if performance is None:
        raise AppException(ErrorCode.PERF_NOT_FOUND)

    prices = [g.price for g in performance.seat_grades]
    price_info = (
        PriceRange(min_price=min(prices), max_price=max(prices))
        if prices
        else PriceRange(min_price=0, max_price=0)
    )

    return PerformanceDetailResponse(
        id=performance.id,
        title=performance.title,
        category=CategorySummary(id=performance.category.id, name=performance.category.name),
        description=performance.description,
        ticket_open_at=performance.ticket_open_at,
        ticket_close_at=performance.ticket_close_at,
        schedules=[_to_schedule_summary(db, s) for s in performance.schedules],
        price_info=price_info,
        running_time_min=performance.running_time_min,
        age_limit=performance.age_limit,
        venue=VenueSummary(
            id=performance.venue.id,
            name=performance.venue.name,
            address=performance.venue.address,
        ),
        seat_grades=[
            SeatGradeInfo(grade=g.grade, price=g.price) for g in performance.seat_grades
        ],
        images=[
            PerformanceImageInfo(
                image_url=build_image_url(img.file_key), sort_order=img.sort_order
            )
            for img in performance.images
        ],
        status=performance.status,
    )


def get_schedule_detail(db, schedule_id):
    schedule = repository.get_schedule_by_id(db, schedule_id)
    if schedule is None:
        raise AppException(ErrorCode.PERF_SCHEDULE_NOT_FOUND)

    performance = schedule.performance
    return ScheduleDetailResponse(
        schedule_id=schedule.id,
        performance_id=performance.id,
        performance_title=performance.title,
        venue_id=performance.venue.id,
        venue_name=performance.venue.name,
        date=schedule.perf_date,
        time=schedule.perf_time,
        seat_grades=_seat_grade_availability(db, schedule.id),
    )


def get_schedules(db, performance_id):
    schedules = repository.list_schedules(db, performance_id)
    result = []
    for schedule in schedules:
        performance = schedule.performance
        status = _schedule_sale_status(
            db, schedule, performance.ticket_open_at, performance.ticket_close_at
        )
        start_at = datetime.combine(schedule.perf_date, schedule.perf_time)
        result.append(ScheduleResponse(id=schedule.id, start_at=start_at, sale_status=status))
    return result
