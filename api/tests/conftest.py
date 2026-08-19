"""
[모듈] api/tests/conftest.py
[담당] A
[역할] 테스트 DB 세션(SQLite 파일) + FastAPI TestClient 픽스처. Valkey는 fakeredis로 대체.

[구현할 것]
- client 픽스처: TestClient(create_app())
- db_session 픽스처: 테스트에서 직접 레포지토리를 호출할 때 쓰는 writer 세션

[의존]
- fakeredis (Valkey 대체)
- app.db.base, app.db.session, app.main

[주의로 추가]
- performance/performance_image/member_favorite는 아직 SQLAlchemy ORM 모델이
  없다(B 담당, raw SQL 우선). Base.metadata.create_all()로는 안 만들어지므로
  이 파일에서 SQLite 호환 DDL로 직접 생성한다. 운영에서는
  api/scripts/sql/sesac_ticket_init.sql이 이 테이블들을 만든다.

[호출자]
- tests/test_auth.py, tests/test_queue.py

[주의]
- 반드시 다른 app.* import보다 먼저 환경변수 설정 + redis.Redis monkeypatch를
  수행해야 한다. app.core.config.get_settings()가 lru_cache이고 app.db.session이
  모듈 최상단에서 즉시 get_settings()를 호출하므로, 첫 import 시점의 환경변수로
  DB URL 등이 고정된다.
- 테스트 세션 전체가 테이블을 공유한다(매 테스트마다 초기화하지 않음). 테스트 간
  데이터 충돌을 피하려면 이메일/schedule_id를 테스트마다 고유하게 쓸 것.
"""

import os
import pathlib

_TEST_DB_PATH = pathlib.Path(__file__).resolve().parent / ".test_db.sqlite3"
if _TEST_DB_PATH.exists():
    _TEST_DB_PATH.unlink()

os.environ.setdefault("DB_WRITER_URL", f"sqlite:///{_TEST_DB_PATH}")
os.environ.setdefault("DB_READER_URL", f"sqlite:///{_TEST_DB_PATH}")
os.environ.setdefault("VALKEY_MASTER_HOST", "localhost")
os.environ.setdefault("VALKEY_REPLICA_HOST", "localhost")
os.environ.setdefault("JWT_SECRET", "test-secret-please-override-32bytes-long")
os.environ.setdefault("COOKIE_SECURE", "false")  # TestClient는 http라 Secure 쿠키가 전송 안 됨

import fakeredis
import redis

redis.Redis = fakeredis.FakeRedis

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.base import Base
from app.db.session import WriterSessionLocal, writer_engine
from app.main import create_app

# performance/performance_image/member_favorite: B의 ORM 모델이 아직 없어
# raw SQL로 직접 생성한다 (테스트 전용, 운영 스키마는 init.sql이 담당).
_EXTRA_TABLES_DDL = """
CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category_id INTEGER,
    description TEXT,
    venue_id INTEGER,
    ticket_open_at DATETIME,
    ticket_close_at DATETIME,
    running_time_min INTEGER,
    age_limit TEXT,
    status TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
CREATE TABLE IF NOT EXISTS performance_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    performance_id INTEGER NOT NULL,
    file_key TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS member_favorite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    performance_id INTEGER NOT NULL,
    created_at DATETIME
);
"""


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=writer_engine)
    with writer_engine.begin() as conn:
        for statement in _EXTRA_TABLES_DDL.strip().split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
    yield
    Base.metadata.drop_all(bind=writer_engine)
    writer_engine.dispose()
    try:
        if _TEST_DB_PATH.exists():
            _TEST_DB_PATH.unlink()
    except PermissionError:
        pass  # Windows에서 sqlite 파일 핸들이 늦게 풀리는 경우가 있음. 다음 실행 시 정리됨.


@pytest.fixture
def client():
    return TestClient(create_app())


@pytest.fixture
def db_session():
    session = WriterSessionLocal()
    try:
        yield session
    finally:
        session.close()
