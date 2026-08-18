"""
[모듈] api/app/cache/keys.py
[담당] 공통
[역할] Valkey 키 문자열을 함수로 캡슐화. A/B가 공유하는 유일한 캐시 키 정의 파일.

[구현할 것]
- refresh_token(member_id) -> str      A: refresh 토큰 저장
- entry_ticket(ticket_id) -> str       A: 대기열 입장 티켓
- queue(schedule_id) -> str            A: 대기열 Sorted Set
- seat_status(schedule_id) -> str      B: 좌석 상태 캐시
- hold(hold_id) -> str                 B: 선점 정보
- worker_lock(name) -> str             공통: 워커 리더 선출 락

[의존]
- 없음

[호출자]
- app.domains.auth.repository (A), app.domains.queue.service (A)
- app.domains.reservation.hold_service (B)
- app.workers.base, app.workers.queue_dispatcher, app.workers.hold_sweeper

[주의]
- A와 B가 공유하는 파일이므로 새 키를 추가할 때는 반드시 상대에게 알릴 것.
  실제 문자열 포맷(prefix, 구분자)은 이 파일 한 곳에서만 정의한다.
"""


def refresh_token(member_id: int) -> str:
    return f"auth:refresh:{member_id}"


def entry_ticket(ticket_id: str) -> str:
    return f"queue:ticket:{ticket_id}"


def queue(schedule_id: int) -> str:
    return f"queue:sorted:{schedule_id}"


def seat_status(schedule_id: int) -> str:
    return f"seat:status:{schedule_id}"


def hold(hold_id: str) -> str:
    return f"seat:hold:{hold_id}"


def worker_lock(name: str) -> str:
    return f"worker:lock:{name}"
