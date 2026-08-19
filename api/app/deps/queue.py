"""
[모듈] api/app/deps/queue.py
[담당] A
[역할] entryTicket 검증 게이트. B의 Hold API가 Depends로 붙여 쓴다.

[구현할 것]
- verify_entry_ticket_value(ticket, member_id) -> None
    entryTicket 문자열과 member_id를 직접 받아 검증하는 순수 함수.
    RESV-003(좌석 임시 선점)처럼 entryTicket이 요청 바디에 실려 오는 경우 사용.
- verify_entry_ticket(x_entry_ticket, member) -> None
    헤더 기반 FastAPI Depends 버전. 내부적으로 verify_entry_ticket_value를 호출.

[의존]
- app.cache.client (master 전용)
- app.cache.keys (entry_ticket)
- app.core.config (QUEUE_ENABLED)
- app.deps.auth (get_current_member)

[호출자]
- app.domains.reservation.hold_service.create_hold (RESV-003, 바디 기반 —
  verify_entry_ticket_value를 직접 호출)

[주의]
- settings.QUEUE_ENABLED가 False면 검증 없이 통과시켜야 한다. 대기열 미완성 시
  예매 데모를 살리는 유일한 보험(우회 플래그).
- api 설계서 RESV-003은 entryTicket을 요청 바디 `{ scheduleId, seatIds, entryTicket }`
  에 담아 보낸다 (헤더가 아님). 그래서 Depends로 자동 주입되는 verify_entry_ticket
  대신, 라우터/서비스가 바디에서 값을 꺼내 verify_entry_ticket_value를 직접 호출한다.
"""

from fastapi import Depends, Header

from app.cache.client import get_master_client
from app.cache.keys import entry_ticket as entry_ticket_key
from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.deps.auth import get_current_member
from app.domains.member.model import Member


def verify_entry_ticket_value(ticket: str | None, member_id: int) -> None:
    settings = get_settings()
    if not settings.queue_enabled:
        return

    if not ticket:
        raise AppException(ErrorCode.QUEUE_ENTRY_TICKET_MISSING)

    client = get_master_client()
    stored_member_id = client.get(entry_ticket_key(ticket))
    if stored_member_id is None or int(stored_member_id) != member_id:
        raise AppException(ErrorCode.QUEUE_ENTRY_TICKET_INVALID)


def verify_entry_ticket(
    x_entry_ticket: str | None = Header(default=None),
    member: Member = Depends(get_current_member),
) -> None:
    verify_entry_ticket_value(x_entry_ticket, member.id)
