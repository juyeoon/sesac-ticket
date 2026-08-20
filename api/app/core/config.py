"""
[모듈] api/app/core/config.py
[담당] 공통
[역할] .env를 읽어 Settings 객체로 노출. DB/Valkey/JWT/예매/대기열 설정값 일원화.

[구현할 것]
- class Settings(BaseSettings): DB/Valkey/JWT/예매/대기열/인스턴스 필드
- get_settings() -> Settings: lru_cache로 싱글턴 반환

[의존]
- pydantic-settings

[호출자]
- 거의 모든 모듈 (writer/reader 접속, JWT, 캐시, 대기열 게이트 등)

[주의]
- QUEUE_ENABLED=false면 deps/queue.py가 entryTicket 검증 없이 통과시키는
  우회 플래그. 대기열이 미완성이어도 예매 데모를 살리는 유일한 보험이므로
  반드시 존재해야 함.
- 필드 추가 시 팀 전체의 로컬 .env.example도 함께 갱신할 것. 임의로 늘리면
  서로의 로컬 환경이 깨짐.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- DB ---
    db_writer_url: str
    db_reader_url: str
    db_pool_size: int = 5
    db_pool_recycle: int = 3600

    # --- Valkey ---
    valkey_master_host: str
    valkey_master_port: int = 6379
    valkey_replica_host: str
    valkey_replica_port: int = 6379

    # --- JWT ---
    jwt_secret: str
    jwt_access_expire_min: int = 30
    jwt_refresh_expire_days: int = 14

    # --- 예매 ---
    hold_ttl_sec: int = 300
    seat_status_cache_ttl_sec: int = 5  # 좌석 상태 조회(RESV-002) 캐시 TTL
    bank_transfer_payment_due_hours: int = 24  # 무통장입금 입금 기한(시간)
    bank_account_info: str = "국민은행 123456-78-901234 (예금주: 새싹티켓)"
    hold_sweep_interval_sec: int = 10  # hold_sweeper 워커 폴링 주기
    reservation_sweep_interval_sec: int = 60  # reservation_sweeper(입금기한 만료) 워커 폴링 주기

    # --- 대기열 ---
    queue_enabled: bool = True
    queue_dispatch_batch_size: int = 50
    queue_poll_interval_sec: int = 3
    queue_token_ttl_sec: int = 1800  # queueToken 유효시간(초). 이 안에 방출 안 되면 만료

    # --- 인증 부가 기능 (비밀번호 재설정 / 이메일 인증) ---
    password_reset_ttl_sec: int = 900  # 재설정 토큰 유효시간 15분
    email_verification_ttl_sec: int = 600  # 인증 코드 유효시간 10분
    email_verification_cooldown_sec: int = 60  # 재요청 쿨다운(429 방지 최소 구현)

    # --- 이메일 발송 (SMTP) ---
    smtp_host: str = ""  # 비어있으면 실제 발송 없이 로그만 남김 (로컬/테스트 기본값)
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    smtp_from_email: str = "no-reply@sesac-ticket.local"
    smtp_from_name: str = "새싹티켓"

    # --- 인프라 ---
    trusted_proxy_hosts: str = "*"  # ALB 2단 구성. 운영에서는 nginx 내부 IP 대역으로 한정할 것
    cookie_secure: bool = True  # refreshToken 쿠키 Secure 플래그. 로컬 http 개발 시 false

    # --- 앱/API 버전 (SYS-003) ---
    api_version: str = "1.0.0"
    app_latest_version: str = "1.0.0"
    app_min_required_version: str = "1.0.0"
    app_force_update: bool = False
    app_update_url: str = ""

    # --- 인스턴스 ---
    instance_id: str = "api-local"
    instance_az: str = "unknown"  # 배포 시 실제 가용영역으로 주입 (예: ap-northeast-2a)


@lru_cache
def get_settings() -> Settings:
    return Settings()
