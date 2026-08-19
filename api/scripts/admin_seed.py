"""
[모듈] api/scripts/admin_seed.py
[담당] B
[역할] Swagger에서 admin 로그인(POST /api/v1/admin/auth/login)을 테스트할 수 있도록
       admin 계정 1개를 시드. admin 회원가입 API가 없어서 DB에 직접 넣어야 함.

[구현할 것]
- seed(engine) -> None: admin_id가 이미 있으면 스킵하고 있는 계정 정보만 안내
- main() -> None: CLI 진입점 (`python -m scripts.admin_seed`)

[의존]
- app.core.security (hash_password) — 평문 비밀번호를 그대로 저장하지 않음
- app.db.session (writer_engine)

[호출자]
- 수동 실행: `cd api && python -m scripts.admin_seed`

[주의]
- 이 스크립트가 만드는 계정은 개발/테스트 전용이다. 운영 DB에는 실행하지 말 것.
- admin_id는 sesac_ticket_dummy_data_1.sql과 동일하게 "admin01"로 맞춰서, 그
  더미 데이터를 이미 넣은 경우와 계정이 겹쳐도 동작하도록 했다 (이미 있으면 skip).
"""

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.core.security import hash_password
from app.db.session import writer_engine

_ADMIN_ID = "admin01"
_ADMIN_PASSWORD = "test1234!"
_ADMIN_NAME = "새싹 관리자"
_ADMIN_ROLE = "SUPER"


def seed(engine: Engine) -> None:
    with engine.begin() as conn:
        existing = conn.execute(
            text("SELECT id FROM admin WHERE admin_id = :admin_id"),
            {"admin_id": _ADMIN_ID},
        ).first()
        if existing:
            print(f"admin '{_ADMIN_ID}'는 이미 있습니다 (id={existing.id}). 새로 만들지 않습니다.")
            return

        conn.execute(
            text(
                "INSERT INTO admin (admin_id, password_hash, name, role, created_at) "
                "VALUES (:admin_id, :password_hash, :name, :role, :created_at)"
            ),
            {
                "admin_id": _ADMIN_ID,
                "password_hash": hash_password(_ADMIN_PASSWORD),
                "name": _ADMIN_NAME,
                "role": _ADMIN_ROLE,
                "created_at": datetime.now(),
            },
        )


def main() -> None:
    seed(writer_engine)
    print(f"admin seed complete: adminId={_ADMIN_ID}, password={_ADMIN_PASSWORD}")


if __name__ == "__main__":
    main()
