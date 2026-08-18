"""
[모듈] api/app/domains/queue/schema.py
[담당] A
[역할] 진입 요청, 순번/상태 응답 DTO.

[구현할 것]
- QueueEnterRequest
- QueueStatusResponse (WAITING/READY 공통 응답 — position, entry_ticket 등)

[의존]
- pydantic

[호출자]
- app.domains.queue.router
"""

from pydantic import BaseModel


class QueueEnterRequest(BaseModel):
    schedule_id: int


class QueueStatusResponse(BaseModel):
    schedule_id: int
    status: str  # WAITING, READY
    position: int
    estimated_wait_sec: int
    entry_ticket: str | None = None
