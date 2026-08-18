"""
[모듈] api/alembic/env.py
[담당] 공통
[역할] Alembic 마이그레이션 환경 설정. registry.py를 참조해 전 테이블을 인식.

[구현할 것]
- run_migrations_offline() -> None
    표준 alembic 오프라인 마이그레이션 (URL만으로 SQL 생성).
- run_migrations_online() -> None
    app.db.registry import 후 target_metadata = Base.metadata 설정,
    settings.DB_WRITER_URL로 접속하여 마이그레이션 실행.

[의존]
- app.db.base (Base)
- app.db.registry (전 도메인 model import)
- app.core.config (DB_WRITER_URL)

[호출자]
- alembic 커맨드 (alembic revision --autogenerate, alembic upgrade head)
- api/scripts/migrate.sh

[주의]
- 반드시 DB_WRITER_URL로만 접속한다. reader/replica URL로 마이그레이션을
  시도하면 안 됨(스키마 변경은 master에서만 발생해야 복제가 정상 동작).

[TODO] 구현 필요
"""

def run_migrations_offline():
    pass


def run_migrations_online():
    pass
