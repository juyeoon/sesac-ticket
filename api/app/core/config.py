"""
[모듈] api/app/core/config.py
[담당] 공통
[역할] .env를 읽어 Settings 객체로 노출. DB/Valkey/JWT/예매/대기열 설정값 일원화.

[구현할 것]
- class Settings(BaseSettings)
    # DB
    - DB_WRITER_URL: str
    - DB_READER_URL: str
    - DB_POOL_SIZE: int
    - DB_POOL_RECYCLE: int = 3600
    # Valkey
    - VALKEY_MASTER_HOST: str
    - VALKEY_MASTER_PORT: int
    - VALKEY_REPLICA_HOST: str
    - VALKEY_REPLICA_PORT: int
    # JWT
    - JWT_SECRET: str
    - JWT_ACCESS_EXPIRE_MIN: int
    - JWT_REFRESH_EXPIRE_DAYS: int
    # 예매
    - HOLD_TTL_SEC: int
    # 대기열
    - QUEUE_ENABLED: bool
    - QUEUE_DISPATCH_BATCH_SIZE: int
    - QUEUE_POLL_INTERVAL_SEC: int
    # 인스턴스
    - INSTANCE_ID: str
- get_settings() -> Settings
    캐시된 Settings 싱글턴 반환 (lru_cache 등)

[의존]
- 없음 (pydantic-settings만 표준 의존)

[호출자]
- 거의 모든 모듈 (writer/reader 접속, JWT, 캐시, 대기열 게이트 등)

[주의]
- QUEUE_ENABLED=false면 deps/queue.py가 entryTicket 검증 없이 통과시키는
  우회 플래그. 대기열이 미완성이어도 예매 데모를 살리는 유일한 보험이므로
  반드시 존재해야 함.
- 필드 추가 시 팀 전체의 로컬 .env.example도 함께 갱신할 것. 임의로 늘리면
  서로의 로컬 환경이 깨짐.

[TODO] 구현 필요
"""

class Settings:
    pass


def get_settings():
    pass
