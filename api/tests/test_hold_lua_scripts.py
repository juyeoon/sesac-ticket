"""
[모듈] api/tests/test_hold_lua_scripts.py
[담당] B (인계받아 A가 구현 진행 — 2026-08-19)
[역할] hold_seats.lua / release_seats.lua의 원자성/소유권 검증 테스트.

[구현할 것]
- test_hold_all_or_nothing_succeeds_when_all_seats_free
- test_hold_fails_completely_if_any_seat_already_locked
- test_release_only_removes_locks_owned_by_the_caller
- test_release_does_not_touch_locks_owned_by_someone_else

[의존]
- tests.conftest (fakeredis monkeypatch가 이미 적용된 상태)
- lupa (fakeredis의 EVAL 지원에 필요 — pyproject.toml dev 의존성)

[호출자]
- pytest

[주의]
- 실제 hold_service(3단계)가 아직 없어서, 이 테스트는 스크립트 자체를
  app.cache.client.get_master_client()로 직접 EVAL해서 검증한다.
"""

import pathlib

from app.cache.client import get_master_client
from app.cache.keys import seat_lock

_SCRIPTS_DIR = pathlib.Path(__file__).resolve().parent.parent / "app" / "cache" / "scripts"
_HOLD_SCRIPT = (_SCRIPTS_DIR / "hold_seats.lua").read_text(encoding="utf-8")
_RELEASE_SCRIPT = (_SCRIPTS_DIR / "release_seats.lua").read_text(encoding="utf-8")


def _hold(client, seat_ids, hold_id, ttl=300):
    keys = [seat_lock(sid) for sid in seat_ids]
    return client.eval(_HOLD_SCRIPT, len(keys), *keys, hold_id, str(ttl))


def _release(client, seat_ids, hold_id):
    keys = [seat_lock(sid) for sid in seat_ids]
    return client.eval(_RELEASE_SCRIPT, len(keys), *keys, hold_id)


def test_hold_all_or_nothing_succeeds_when_all_seats_free():
    client = get_master_client()
    result = _hold(client, [101, 102, 103], "hold-1")
    assert result == 1
    for sid in (101, 102, 103):
        assert client.get(seat_lock(sid)) == "hold-1"


def test_hold_fails_completely_if_any_seat_already_locked():
    client = get_master_client()
    _hold(client, [201], "hold-a")

    result = _hold(client, [201, 202], "hold-b")

    assert result == 0
    assert client.get(seat_lock(202)) is None  # all-or-nothing: 다른 좌석도 세팅되면 안 됨
    assert client.get(seat_lock(201)) == "hold-a"  # 기존 락 유지


def test_release_only_removes_locks_owned_by_the_caller():
    client = get_master_client()
    _hold(client, [301, 302], "hold-owner")

    released = _release(client, [301, 302], "hold-owner")

    assert released == 2
    assert client.get(seat_lock(301)) is None
    assert client.get(seat_lock(302)) is None


def test_release_does_not_touch_locks_owned_by_someone_else():
    client = get_master_client()
    _hold(client, [401], "hold-real-owner")

    released = _release(client, [401], "hold-imposter")

    assert released == 0
    assert client.get(seat_lock(401)) == "hold-real-owner"  # 그대로 남아있어야 함
