"""
[모듈] api/alembic/env.py
[담당] 공통
[역할] Alembic 마이그레이션 환경 설정. registry.py를 참조해 전 테이블을 인식.

[구현할 것]
- run_migrations_offline() -> None
- run_migrations_online() -> None

[의존]
- app.db.base (Base)
- app.db.registry (전 도메인 model import)
- app.core.config (DB_WRITER_URL)

[호출자]
- alembic 커맨드 (alembic stamp, alembic revision --autogenerate, alembic upgrade head)
- api/scripts/migrate.sh

[주의]
- 반드시 DB_WRITER_URL로만 접속한다. reader/replica URL로 마이그레이션을
  시도하면 안 됨(스키마 변경은 master에서만 발생해야 복제가 정상 동작).
- 최초 스키마는 Alembic이 만들지 않는다. api/scripts/sql/sesac_ticket_init.sql을
  직접 실행한 뒤 `alembic stamp head`로 현재 상태를 등록하는 방식(raw SQL 우선)을
  쓰기로 했다 (2026-08-18 결정). 이후 스키마 변경부터 `alembic revision --autogenerate`
  로 diff를 쌓는다.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db import registry  # noqa: F401  (전 도메인 model import 트리거)
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

_settings = get_settings()
config.set_main_option("sqlalchemy.url", _settings.db_writer_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
