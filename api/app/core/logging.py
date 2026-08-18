"""
[모듈] api/app/core/logging.py
[담당] 공통
[역할] JSON 로그 포맷 설정. instance_id 필드를 포함해 인스턴스별 로그 구분.

[구현할 것]
- setup_logging() -> None
    JSON 포맷 핸들러 설정. 각 로그 레코드에 instance_id 필드 삽입.
- get_logger(name: str) -> Logger
    모듈별 로거 반환.

[의존]
- app.core.config (INSTANCE_ID)

[호출자]
- app.main (create_app에서 최초 1회 호출)
- app.core.lifespan
- 전 도메인 service (필요 시)

[주의]
- api 인스턴스가 2대(api-a / api-c) 운영되므로 instance_id 없이는 로그가
  어느 인스턴스에서 발생했는지 구분 불가. 장애 추적의 최소 조건.

[TODO] 구현 필요
"""

def setup_logging():
    pass


def get_logger(name):
    pass
