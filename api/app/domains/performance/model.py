from datetime import date, datetime, time

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base, TimestampMixin


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class Performance(Base, TimestampMixin):
    __tablename__ = "performance"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    description: Mapped[str | None] = mapped_column(Text)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venue.id"))
    ticket_open_at: Mapped[datetime | None]
    ticket_close_at: Mapped[datetime | None]
    running_time_min: Mapped[int | None]
    age_limit: Mapped[str | None]
    status: Mapped[str]

    category: Mapped["Category"] = relationship()
    venue: Mapped["Venue"] = relationship()
    images: Mapped[list["PerformanceImage"]] = relationship(
        order_by="PerformanceImage.sort_order"
    )
    seat_grades: Mapped[list["PerformanceSeatGrade"]] = relationship()
    schedules: Mapped[list["Schedule"]] = relationship(
        back_populates="performance", order_by="Schedule.perf_date, Schedule.perf_time"
    )


class PerformanceImage(Base):
    __tablename__ = "performance_image"

    id: Mapped[int] = mapped_column(primary_key=True)
    performance_id: Mapped[int] = mapped_column(ForeignKey("performance.id"))
    file_key: Mapped[str]
    sort_order: Mapped[int] = mapped_column(default=0)


class PerformanceSeatGrade(Base):
    __tablename__ = "performance_seat_grade"

    id: Mapped[int] = mapped_column(primary_key=True)
    performance_id: Mapped[int] = mapped_column(ForeignKey("performance.id"))
    grade: Mapped[str]
    price: Mapped[int]


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True)
    performance_id: Mapped[int] = mapped_column(ForeignKey("performance.id"))
    perf_date: Mapped[date]
    perf_time: Mapped[time]
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    performance: Mapped["Performance"] = relationship(back_populates="schedules")
