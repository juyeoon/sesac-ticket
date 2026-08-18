"""
[모듈] api/app/domains/queue/schema.py
[담당] A
[역할] 진입 요청/응답, 상태 조회 응답 DTO. api 설계서 TRF-001/002 규격(camelCase)을 따른다.

[구현할 것]
- QueueEnterRequest ({ performanceId, scheduleId })
- QueueEnterResponse ({ queueToken, position, estimatedWaitSeconds })
- QueueStatusResponse ({ status, position, estimatedWaitSeconds, entryTicket })

[의존]
- pydantic

[호출자]
- app.domains.queue.router
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class QueueEnterRequest(_CamelModel):
    performance_id: int
    schedule_id: int


class QueueEnterResponse(_CamelModel):
    queue_token: str
    position: int
    estimated_wait_seconds: int


class QueueStatusResponse(_CamelModel):
    status: str  # WAITING, READY
    position: int
    estimated_wait_seconds: int
    entry_ticket: str | None = None
