"""
[모듈] api/app/db/registry.py
[담당] 공통
[역할] 전 도메인 model.py를 import만 하는 파일. Alembic이 테이블을 인식하는 유일한 경로.

[구현할 것]
- (import 전용 파일. 함수 없음)
    아래 A 담당 영역 / B 담당 영역에 각자 자기 도메인 model만 한 줄씩 추가한다.

[의존]
- 전 도메인 model.py (A: member/admin, B: venue/performance/reservation/payment)

[호출자]
- api/alembic/env.py (target_metadata = Base.metadata 구성 시 이 파일을 import)

[주의]
- 이 파일은 A와 B가 공동으로 수정하는 유일한 파일 중 하나이다. 반드시
  자기 구역 안에만 줄을 추가할 것. 여기 빠지면 Alembic이 해당 테이블을
  통째로 누락한다.
- 두 사람이 각자 자기 구역에만 줄을 추가하면 git merge 시 서로 다른 줄이라
  충돌이 나지 않는다. 구역을 벗어나 추가하면 충돌 위험이 커진다.

[TODO] 구현 필요
"""

# --- A 담당 영역 (아래에만 추가) ---
# from app.domains.member.model import Member
# from app.domains.admin.model import Admin

# --- B 담당 영역 (아래에만 추가) ---
# from app.domains.venue.model import Venue, VenueSeat
# from app.domains.performance.model import Performance
# from app.domains.reservation.model import Reservation
