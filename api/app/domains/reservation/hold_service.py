"""
[모듈] api/app/domains/reservation/hold_service.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] 좌석 임시 선점 생성/해제/상태조회. api 설계서 RESV-003, 012, 013에 대응.

[구현할 것]
- create_hold(db, *, member_id, schedule_id, seat_ids, entry_ticket) -> HoldResult
- release_hold(db, *, hold_id, member_id) -> None
- get_hold(*, hold_id, member_id) -> HoldDetail
- expire_hold(db, hold_log) -> None
    workers.hold_sweeper 전용. release_hold와 달리 소유자 검증이 없다 — TTL이
    지난 hold를 시스템이 강제로 되돌리는 것이므로 member_id 대조가 의미 없음.

[의존]
- app.deps.queue.verify_entry_ticket_value (entryTicket 검증 — RESV-003은 바디로 옴)
- app.domains.reservation.repository (DB 접근)
- app.cache.client (get_master_client, eval_with_fallback)
- app.cache.keys (seat_lock, hold)
- app.core.config (HOLD_TTL_SEC)
- app.core.exceptions

[호출자]
- app.domains.reservation.router

[주의]
- 좌석 상태가 바뀔 때(선점/해제)마다 service.invalidate_seat_status_cache()를
  호출해 RESV-002 캐시(seat:status:{scheduleId})를 무효화한다 — 다음 조회에서
  DB의 최신 상태로 다시 채워지게 하기 위함.
- Lua 스크립트(hold_seats.lua/release_seats.lua)가 최종 원자성을 보장하지만,
  그 전에 DB에서 좌석이 실제 존재하고 AVAILABLE인지 먼저 확인한다 (빠른 실패).
- create_hold는 요청 좌석 수가 MAX_SEATS_PER_HOLD(기본 2)를 넘으면 다른 검증보다
  먼저 RESV_SEAT_LIMIT_EXCEEDED(400)로 거절한다 — DB 스키마 변경 없이 API 레벨
  검증만으로 처리 (프론트Q-백엔드-답변.md #5 결정).
- Hold 세션 정보는 Valkey `seat:hold:{holdId}`에 JSON으로 저장하고 TTL을 건다
  (밸키 키 설계서 규격). get_hold()는 이 캐시를 우선 사용해 DB 왕복 없이 빠르게
  응답한다 — 없으면(만료/미존재) 404.
- 스크립트 SHA는 core/lifespan.py가 앱 기동 시 SCRIPT LOAD한 결과와 항상 같다
  (SHA1은 스크립트 바이트에 대해 결정적이므로, 여기서 Python으로 직접 계산해도
  서버가 이미 로드해둔 스크립트와 매칭된다 — app.state에 의존할 필요 없음).
- 반드시 get_db(writer)로만 호출한다.
"""

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.cache.client import eval_with_fallback, get_master_client
from app.cache.keys import hold as hold_key
from app.cache.keys import seat_lock
from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.deps.queue import verify_entry_ticket_value
from app.domains.reservation import repository
from app.domains.reservation.model import SeatHoldLog
from app.domains.reservation.service import invalidate_seat_status_cache

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "cache" / "scripts"
_HOLD_SCRIPT = (_SCRIPTS_DIR / "hold_seats.lua").read_text(encoding="utf-8")
_RELEASE_SCRIPT = (_SCRIPTS_DIR / "release_seats.lua").read_text(encoding="utf-8")
_HOLD_SCRIPT_SHA = hashlib.sha1(_HOLD_SCRIPT.encode("utf-8")).hexdigest()
_RELEASE_SCRIPT_SHA = hashlib.sha1(_RELEASE_SCRIPT.encode("utf-8")).hexdigest()


@dataclass
class HoldResult:
    hold_id: str
    seat_ids: list[int]
    expires_at: datetime


@dataclass
class HoldDetail:
    hold_id: str
    seat_ids: list[int]
    expires_at: datetime
    remaining_seconds: int


def create_hold(
    db: Session,
    *,
    member_id: int,
    schedule_id: int,
    seat_ids: list[int],
    entry_ticket: str | None,
) -> HoldResult:
    settings = get_settings()
    if len(seat_ids) > settings.max_seats_per_hold:
        raise AppException(ErrorCode.RESV_SEAT_LIMIT_EXCEEDED)

    verify_entry_ticket_value(entry_ticket, member_id)

    seats = repository.get_seats_for_hold(db, schedule_id=schedule_id, seat_ids=seat_ids)
    if len(seats) != len(seat_ids):
        raise AppException(ErrorCode.RESV_SEAT_NOT_FOUND)
    if any(seat.status != "AVAILABLE" for seat in seats):
        raise AppException(ErrorCode.RESV_SEAT_ALREADY_HELD)

    hold_id = uuid.uuid4().hex
    lock_keys = [seat_lock(sid) for sid in seat_ids]

    client = get_master_client()
    result = eval_with_fallback(
        client,
        _HOLD_SCRIPT_SHA,
        _HOLD_SCRIPT,
        lock_keys,
        [hold_id, str(settings.hold_ttl_sec)],
    )
    if result != 1:
        raise AppException(ErrorCode.RESV_SEAT_ALREADY_HELD)

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.hold_ttl_sec)

    repository.mark_seats_held(db, seat_ids)
    repository.create_seat_hold_log(
        db,
        hold_id=hold_id,
        member_id=member_id,
        schedule_id=schedule_id,
        seat_ids=seat_ids,
        expires_at=expires_at,
    )

    session_payload = json.dumps(
        {
            "member_id": member_id,
            "schedule_id": schedule_id,
            "seat_ids": seat_ids,
            "expires_at": expires_at.isoformat(),
        }
    )
    client.set(hold_key(hold_id), session_payload, ex=settings.hold_ttl_sec)
    invalidate_seat_status_cache(schedule_id)

    return HoldResult(hold_id=hold_id, seat_ids=seat_ids, expires_at=expires_at)


def _load_session(hold_id: str) -> dict | None:
    client = get_master_client()
    raw = client.get(hold_key(hold_id))
    if raw is None:
        return None
    return json.loads(raw)


def release_hold(db: Session, *, hold_id: str, member_id: int) -> None:
    hold_log = repository.get_seat_hold_log(db, hold_id)
    if hold_log is None:
        raise AppException(ErrorCode.RESV_HOLD_NOT_FOUND)
    if hold_log.status != "HOLDING":
        raise AppException(ErrorCode.RESV_HOLD_EXPIRED)
    if hold_log.member_id != member_id:
        raise AppException(ErrorCode.RESV_HOLD_OWNER_MISMATCH)

    client = get_master_client()
    lock_keys = [seat_lock(sid) for sid in hold_log.schedule_seat_ids]
    eval_with_fallback(client, _RELEASE_SCRIPT_SHA, _RELEASE_SCRIPT, lock_keys, [hold_id])
    client.delete(hold_key(hold_id))

    repository.mark_seats_available(db, hold_log.schedule_seat_ids)
    repository.mark_hold_released(db, hold_log)
    invalidate_seat_status_cache(hold_log.schedule_id)


def expire_hold(db: Session, hold_log: SeatHoldLog) -> None:
    client = get_master_client()
    lock_keys = [seat_lock(sid) for sid in hold_log.schedule_seat_ids]
    eval_with_fallback(client, _RELEASE_SCRIPT_SHA, _RELEASE_SCRIPT, lock_keys, [hold_log.hold_id])
    client.delete(hold_key(hold_log.hold_id))

    repository.mark_seats_available(db, hold_log.schedule_seat_ids)
    repository.mark_hold_expired(db, hold_log)
    invalidate_seat_status_cache(hold_log.schedule_id)


def get_hold(*, hold_id: str, member_id: int) -> HoldDetail:
    session = _load_session(hold_id)
    if session is None:
        raise AppException(ErrorCode.RESV_HOLD_NOT_FOUND)
    if session["member_id"] != member_id:
        raise AppException(ErrorCode.RESV_HOLD_OWNER_MISMATCH)

    client = get_master_client()
    remaining = client.ttl(hold_key(hold_id))
    if remaining is None or remaining < 0:
        raise AppException(ErrorCode.RESV_HOLD_NOT_FOUND)

    expires_at = datetime.fromisoformat(session["expires_at"])
    return HoldDetail(
        hold_id=hold_id,
        seat_ids=session["seat_ids"],
        expires_at=expires_at,
        remaining_seconds=remaining,
    )
