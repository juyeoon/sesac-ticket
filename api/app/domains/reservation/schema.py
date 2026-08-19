"""
[모듈] api/app/domains/reservation/schema.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 예매 도메인 응답 DTO. api 설계서 규격(camelCase)을 따른다.

[구현할 것]
- SeatStatusItem ({ seatId, section, row, number, grade, status }) — RESV-002

[의존]
- pydantic

[호출자]
- app.domains.reservation.service, router
"""

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
