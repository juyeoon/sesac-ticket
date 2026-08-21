# File Ownership

> 아직 도메인 파일이 생성되지 않은 시점의 원칙만 정리. 파일이 추가되면 표를 채운다.

## 담당 원칙

| 담당 | 범위 |
|---|---|
| A | `domains/auth`, `domains/member`, `domains/admin`, `domains/queue`, `domains/system`, `deps/auth.py`, `deps/queue.py`, `workers/queue_dispatcher.py`, `scripts/seed.py` |
| B | `domains/venue`, `domains/performance`, `domains/reservation`, `domains/payment`, `workers/base.py`, `workers/hold_sweeper.py`, `cache/scripts/*.lua` |
| 공통 | `core/*`, `db/base.py`, `db/session.py`, `db/routing.py`, `db/registry.py`(구역별), `cache/client.py`, `cache/keys.py`, `api/v1.py`(구역별), `docs/api-contract.md` |

## 공통 파일 수정 규칙

- 공통 파일 수정이 필요하면 **먼저 상대에게 말하고 수정**한다. 말없이 고치면 상대 로컬이 깨진다.
- `db/registry.py`, `api/v1.py`는 유일하게 양쪽이 함께 건드리는 파일이며, **자기 구역 줄만** 추가한다.
- `pyproject.toml` 의존성 추가는 A에게 요청한다 (락파일 충돌 방지).

## 파일 표 (도메인 파일 생성 후 채울 것)

| 파일 | 담당 | 상태 |
|---|---|---|
| (P0 완료 후 PA/PB 실행 시 갱신) | | |
