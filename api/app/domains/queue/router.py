"""
[모듈] api/app/domains/queue/router.py
[담당] A
[역할] 진입 / 상태(순번) 조회 두 개. model·repository 없음(테이블 안 씀).

[구현할 것]
- POST /queue/enter -> QueueStatusResponse
- GET /queue/status?schedule_id= -> QueueStatusResponse

[의존]
- app.domains.queue.service
- app.deps.auth (get_current_member)

[호출자]
- app.api.v1
"""

from fastapi import APIRouter, Depends

from app.deps.auth import get_current_member
from app.domains.member.model import Member
from app.domains.queue import service as queue_service
from app.domains.queue.schema import QueueEnterRequest, QueueStatusResponse

router = APIRouter(prefix="/queue", tags=["queue"])


@router.post("/enter", response_model=QueueStatusResponse)
def enter_queue(
    request: QueueEnterRequest, member: Member = Depends(get_current_member)
) -> QueueStatusResponse:
    result = queue_service.enter(request.schedule_id, member.id)
    return QueueStatusResponse(**result)


@router.get("/status", response_model=QueueStatusResponse)
def get_status(
    schedule_id: int, member: Member = Depends(get_current_member)
) -> QueueStatusResponse:
    result = queue_service.get_status(schedule_id, member.id)
    return QueueStatusResponse(**result)
