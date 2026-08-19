"""
[모듈] api/app/domains/venue/schema.py
[담당] B
[역할] 좌석 배치도(좌표) 응답 DTO.

[구현할 것]
- class SeatCoordinate(BaseModel)
    seat_id, row, number, x, y, grade 필드. api명세서.xlsx의 PERF-005 응답
    필드명 기준(seatId/row/number — 이전에 id/rowNo/seatNo로 적었던 건 오기).
    section은 여기 없음 — SeatMapSection의 그룹 키로 빠졌다.
- class SeatMapSection(BaseModel)
    section_name, seats: list[SeatCoordinate] 필드. 구역 하나에 속한 좌석들.
- class VenueSeatMapResponse(BaseModel)
    venue_id, sections: list[SeatMapSection] 필드. 좌석을 구역별로 그룹핑한
    구조(스펙 기준 — 이전엔 seats 평면 리스트였는데 이건 오기).

[의존]
- pydantic

[호출자]
- app.domains.venue.router (좌석 배치도 API 응답, GET /venues/{venue_id}/seat-map)

[주의]
- 이 DTO에는 좌석의 실시간 상태(AVAILABLE/HELD/RESERVED — SOLD는 없음)와
  가격이 없다. api명세서.xlsx 비고 기준: 좌표 데이터는 정적이라 CDN/캐시
  적용 대상이고, 실시간 상태/가격은 RESV-002(회차별 좌석 상태 조회)에서
  받아 프런트가 병합한다. scheduleId 쿼리 파라미터가 있어도 이 응답 구조는
  안 바뀐다(router.py 참고).
- JSON은 camelCase(sectionName, seatId 등)다. performance/schema.py의
  CamelModel과 동일한 패턴을 여기서도 별도로 둔다(cross-domain import를
  피하려고 중복). 이 패턴이 계속 쓰이면 나중에 공용 위치(예: app/core 또는
  신설 공용 파일)로 옮기는 걸 A와 상의할 것.

[TODO] 없음 (구현 완료)
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class SeatCoordinate(CamelModel):
    seat_id: int
    row: str
    number: int
    x: int | None = None
    y: int | None = None
    grade: str


class SeatMapSection(CamelModel):
    section_name: str
    seats: list[SeatCoordinate]


class VenueSeatMapResponse(CamelModel):
    venue_id: int
    sections: list[SeatMapSection]
