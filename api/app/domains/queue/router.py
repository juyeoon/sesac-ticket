"""
[모듈] api/app/domains/queue/router.py
[담당] A
[역할] 진입 / 상태(순번) 조회 두 개 (api 설계서 TRF-001/002). model·repository 없음.

[구현할 것]
- POST /queue/enter -> QueueEnterResponse (인증 필요)
- GET /queue/{queue_token}/status -> QueueStatusResponse (인증 불필요)

[의존]
- app.domains.queue.service
- app.deps.auth (get_current_member, 진입 시에만 사용)

[호출자]
- app.api.v1

[주의]
- 순번 조회는 설계서상 인증이 필요 없다 — queueToken 자체가 자격증명이므로
  get_current_member를 붙이지 않는다.
"""

from fastapi import APIRouter, Depends

from app.deps.auth import get_current_member
from app.domains.member.model import Member
from app.domains.queue import service as queue_service
from app.domains.queue.schema import (
    QueueEnterRequest,
    QueueEnterResponse,
    QueueStatusResponse,
)

router = APIRouter(prefix="/queue", tags=["queue"])


@router.post("/enter", response_model=QueueEnterResponse)
def enter_queue(
    request: QueueEnterRequest, member: Member = Depends(get_current_member)
) -> QueueEnterResponse:
    result = queue_service.enter(request.performance_id, request.schedule_id, member.id)
    return QueueEnterResponse(**result)


@router.get("/{queue_token}/status", response_model=QueueStatusResponse)
def get_status(queue_token: str) -> QueueStatusResponse:
    result = queue_service.get_status(queue_token)
    return QueueStatusResponse(**result)
