"""
[모듈] api/app/deps/queue.py
[담당] A
[역할] entryTicket 검증 게이트. B의 Hold API가 Depends로 붙여 쓴다.

[구현할 것]
- verify_entry_ticket(x_entry_ticket, member) -> None
    헤더의 entryTicket이 현재 로그인한 회원 것과 일치하는지 검증.

[의존]
- app.cache.client (master 전용)
- app.cache.keys (entry_ticket)
- app.core.config (QUEUE_ENABLED)
- app.deps.auth (get_current_member)

[호출자]
- app.domains.reservation.router (B 담당) — Hold 생성 엔드포인트

[주의]
- settings.QUEUE_ENABLED가 False면 검증 없이 통과시켜야 한다. 대기열 미완성 시
  예매 데모를 살리는 유일한 보험(우회 플래그).
"""

from fastapi import Depends, Header

from app.cache.client import get_master_client
from app.cache.keys import entry_ticket as entry_ticket_key
from app.core.config import get_settings
from app.core.exceptions import AppException, ErrorCode
from app.deps.auth import get_current_member
from app.domains.member.model import Member


def verify_entry_ticket(
    x_entry_ticket: str | None = Header(default=None),
    member: Member = Depends(get_current_member),
) -> None:
    settings = get_settings()
    if not settings.queue_enabled:
        return

    if not x_entry_ticket:
        raise AppException(ErrorCode.QUEUE_ENTRY_TICKET_MISSING)

    client = get_master_client()
    stored_member_id = client.get(entry_ticket_key(x_entry_ticket))
    if stored_member_id is None or int(stored_member_id) != member.id:
        raise AppException(ErrorCode.QUEUE_ENTRY_TICKET_INVALID)
