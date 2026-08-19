"""
[모듈] api/app/domains/reservation/service.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 좌석 상태 조회 (RESV-002). Valkey Hash 캐시로 조회 부하 감소.

[구현할 것]
- get_seat_status_list(db, schedule_id) -> list[SeatStatusItem]
- invalidate_seat_status_cache(schedule_id) -> None
    Hold 생성/해제 시 캐시를 무효화해 다음 조회에서 최신 상태로 재구성되게 한다.

[의존]
- app.cache.client (get_master_client)
- app.cache.keys (seat_status)
- app.core.config (SEAT_STATUS_CACHE_TTL_SEC)
- app.domains.reservation.repository

[호출자]
- app.domains.reservation.router (RESV-002)
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
"""

from sqlalchemy.orm import Session

from app.cache.client import get_master_client
from app.cache.keys import seat_status as seat_status_key
from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.domains.reservation import repository
from app.domains.reservation.schema import SeatStatusItem


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
