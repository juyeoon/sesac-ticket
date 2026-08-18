"""
[모듈] api/app/core/security.py
[담당] 공통
[역할] JWT 생성·검증, bcrypt 해싱. 도메인 로직 없는 순수 함수만.

[구현할 것]
- hash_password(raw_password: str) -> str
    bcrypt 해시 생성.
- verify_password(raw_password: str, password_hash: str) -> bool
    평문과 해시 비교.
- create_access_token(member_id: int) -> str
    JWT access 토큰 발급. 만료는 settings.JWT_ACCESS_EXPIRE_MIN.
- create_refresh_token(member_id: int) -> str
    JWT refresh 토큰 발급. 만료는 settings.JWT_REFRESH_EXPIRE_DAYS.
- decode_token(token: str) -> dict | None
    서명·만료 검증 후 payload 반환. 실패 시 None.

[의존]
- app.core.config (JWT_SECRET, 만료 시간)

[호출자]
- app.domains.auth.service (A 담당)
- app.deps.auth (A 담당)

[주의]
- 회원 조회, refresh 토큰 저장 등 도메인 지식을 갖지 않는다. 순수 암호화/토큰
  함수만 유지해야 auth 도메인과 책임이 겹치지 않음.

[TODO] 구현 필요
"""

def hash_password(raw_password):
    pass


def verify_password(raw_password, password_hash):
    pass


def create_access_token(member_id):
    pass


def create_refresh_token(member_id):
    pass


def decode_token(token):
    pass
