"""
[모듈] api/app/cache/keys.py
[담당] 공통
[역할] Valkey 키 문자열을 함수로 캡슐화. A/B가 공유하는 유일한 캐시 키 정의 파일.

[구현할 것]
- refresh_token(member_id: int) -> str
    A: refresh 토큰 저장 키.
- entry_ticket(ticket_id: str) -> str
    A: 대기열 입장 티켓 키.
- queue(schedule_id: int) -> str
    A: 대기열 Sorted Set 키.
- seat_status(schedule_id: int) -> str
    B: 좌석 상태 캐시 키.
- hold(hold_id: str) -> str
    B: 선점 정보 키.
- worker_lock(name: str) -> str
    공통: 워커 리더 선출 분산 락 키.

[의존]
- 없음

[호출자]
- app.domains.auth.repository (A), app.domains.queue.service (A)
- app.domains.reservation.hold_service (B)
- app.workers.base, app.workers.queue_dispatcher, app.workers.hold_sweeper

[주의]
- A와 B가 공유하는 파일이므로 새 키를 추가할 때는 반드시 상대에게 알릴 것.
  실제 문자열 포맷(prefix, 구분자)은 이 파일 한 곳에서만 정의한다.

[TODO] 구현 필요
"""

def refresh_token(member_id):
    pass


def entry_ticket(ticket_id):
    pass


def queue(schedule_id):
    pass


def seat_status(schedule_id):
    pass


def hold(hold_id):
    pass


def worker_lock(name):
    pass
