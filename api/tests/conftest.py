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

import fakeredis
import redis

redis.Redis = fakeredis.FakeRedis

import pytest
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import WriterSessionLocal, writer_engine
from app.main import create_app


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=writer_engine)
    yield
    Base.metadata.drop_all(bind=writer_engine)
    writer_engine.dispose()
    if _TEST_DB_PATH.exists():
        _TEST_DB_PATH.unlink()


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
