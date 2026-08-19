"""
[모듈] api/app/domains/venue/repository.py
[담당] B
[역할] 공연장 조회 및 좌석 배치도(물리적 좌표) 조회.

[구현할 것]
- get_venue(db, venue_id: int) -> Venue | None
    공연장 존재 확인용. 없으면 None(router/service에서 404 처리).
- get_seats_by_venue(db, venue_id: int) -> list[VenueSeat]
    해당 공연장의 전체 좌석 좌표·구역·등급 목록을 조회한다.

[의존]
- app.domains.venue.model
- app.db.routing (get_read_db)

[호출자]
- app.domains.venue.router

[주의]
- 읽기 전용. 반드시 get_read_db(reader)를 사용한다.
- 좌석의 실시간 판매 상태는 이 repository의 책임이 아니다. 물리적 좌표만
  반환하고, 상태는 reservation 쪽 조회 결과와 조합해서 응답을 조립한다.

[TODO] 없음 (구현 완료)
"""

from sqlalchemy import Integer, cast, select

from app.domains.venue.model import Venue, VenueSeat


def get_venue(db, venue_id):
    return db.get(Venue, venue_id)


def get_seats_by_venue(db, venue_id):
    # row_no는 varchar 컬럼이라 문자열 정렬하면 "1","10","2"... 순으로 꼬인다.
    # 숫자로 캐스팅해서 정렬한다.
    stmt = (
        select(VenueSeat)
        .where(VenueSeat.venue_id == venue_id)
        .order_by(VenueSeat.section, cast(VenueSeat.row_no, Integer), VenueSeat.seat_no)
    )
    return list(db.scalars(stmt).all())
