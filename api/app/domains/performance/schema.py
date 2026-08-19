from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CategorySummary(CamelModel):
    id: int
    name: str


class VenueSummary(CamelModel):
    id: int
    name: str
    address: str | None = None


class SeatGradeInfo(CamelModel):
    grade: str
    price: int


class PerformanceImageInfo(CamelModel):
    image_url: str
    sort_order: int


class SeatGradeAvailability(CamelModel):
    grade: str
    price: int
    remaining: int


class ScheduleSummary(CamelModel):
    schedule_id: int
    date: date
    time: time
    seat_grades: list[SeatGradeAvailability]


class PriceRange(CamelModel):
    min_price: int
    max_price: int


class PerformanceSummary(CamelModel):
    id: int
    title: str
    thumbnail_url: str | None = None
    category: CategorySummary
    venue: VenueSummary
    date_from: date | None = None
    date_to: date | None = None
    ticket_open_at: datetime | None = None
    ticket_close_at: datetime | None = None
    status: str


class PerformanceListEnvelope(CamelModel):
    content: list[PerformanceSummary]
    total_elements: int


class PerformanceDetailResponse(CamelModel):
    id: int
    title: str
    category: CategorySummary
    description: str | None = None
    ticket_open_at: datetime | None = None
    ticket_close_at: datetime | None = None
    schedules: list[ScheduleSummary]
    price_info: PriceRange
    running_time_min: int | None = None
    age_limit: str | None = None
    venue: VenueSummary
    seat_grades: list[SeatGradeInfo]
    images: list[PerformanceImageInfo]


class ScheduleResponse(CamelModel):
    id: int
    start_at: datetime
    sale_status: str
