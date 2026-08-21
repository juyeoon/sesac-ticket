# 대기열 상태 전이 & 폴링 정책

> api 설계서 TRF-001(대기열 진입)/TRF-002(순번 조회) 규격에 맞춰 queueToken 기반으로
> 재설계함 (2026-08-18). 순번 조회는 **인증이 필요 없다** — queueToken 자체가 자격증명.

## 식별자 정리

| 토큰 | 발급 시점 | 용도 |
|---|---|---|
| `queueToken` | `POST /queue/enter` 성공 시 | 대기열 내 내 위치를 추적하는 키. 이후 상태 조회(`GET /queue/{queueToken}/status`)에 사용 |
| `entryTicket` | 방출(dispatch) 시 | 대기열 통과 증표. B의 Hold API 호출 시 `X-Entry-Ticket` 헤더로 제출 (`deps.queue.verify_entry_ticket`이 검증) |

## 상태 전이

| 상태 | 설명 | 전이 조건 | 저장 위치 |
|---|---|---|---|
| WAITING | 대기열 진입, 순번 대기 중 | `POST /queue/enter` 호출 시 진입 | Valkey Sorted Set `queue:{performanceId}:{scheduleId}` (member=queueToken) |
| READY | 방출되어 입장 가능, entryTicket 발급됨 | `workers.queue_dispatcher.dispatch_once()`가 `ZPOPMIN`으로 방출 | `queue:ready:{queueToken}` → ticket_id (TTL 300초), `queue:ticket:{ticket_id}` → member_id (TTL 300초) |
| ENTERED | entryTicket으로 Hold/예매에 성공, 실질적으로 대기열을 벗어남 | B의 예매 도메인이 `deps.queue.verify_entry_ticket`으로 검증 후 Hold 생성 성공 | 별도 저장 없음 — entryTicket TTL 만료 전에 Hold가 성공했는지로 판단 |
| EXPIRED | READY 상태에서 entryTicket TTL(300초)이 지나도록 미사용, 또는 queueToken 자체가 TTL(`QUEUE_TOKEN_TTL_SEC`, 기본 1800초) 만료 | Valkey TTL 자연 만료 | - |

## queueToken 매핑

`queue:token:{queueToken}` → `"memberId:performanceId:scheduleId"` (TTL `QUEUE_TOKEN_TTL_SEC`).
순번 조회 시 이 매핑에서 performanceId/scheduleId를 복원해 Sorted Set에서 순위를 다시 계산한다.
매핑이 없으면(만료되었거나 애초에 존재한 적 없으면) `404 QUEUE_NOT_ENTERED`.

## 폴링 정책

- 클라이언트는 `GET /queue/{queueToken}/status`를 **`QUEUE_POLL_INTERVAL_SEC`(기본 3초) 간격으로 폴링**한다.
- 이 엔드포인트는 **인증 헤더가 필요 없다.** queueToken을 아는 것 자체가 자격증명이다.
- **롱폴링/SSE/WebSocket 금지.** ALB가 2단(alb-pub → nginx → alb-int → gunicorn) 구성이라 idle timeout(기본 60초) 설정 지점이 두 곳이고, 연결이 예기치 않게 끊길 수 있다. (설계서 비고란은 SSE/WebSocket 검토를 언급하지만, 인프라 제약상 폴링으로 구현함.)
- 응답에 `entryTicket`이 채워지면(`status: "READY"`) 클라이언트는 그 값을 `X-Entry-Ticket` 헤더에 담아 예매 Hold API를 호출한다.

## 예상 대기시간 계산

`estimatedWaitSeconds = position * QUEUE_POLL_INTERVAL_SEC` 로 근사한다 (`domains/queue/service.py`). 실제 처리 속도(디스패처가 실제로 몇 명씩, 얼마나 자주 방출하는지)는 반영하지 않는 고정 계수 근사치다.

## 방출(디스패치) 정책

- `workers/queue_dispatcher.dispatch_once(performance_id, schedule_id)`가 `ZPOPMIN`으로 앞쪽 `QUEUE_DISPATCH_BATCH_SIZE`개(기본 50개) queueToken을 꺼내 entryTicket을 발급한다.
- 주기 실행은 `workers/base.run_as_leader()`(Valkey 분산 락 기반 리더 선출)로 api 인스턴스 2대 중 한쪽만 수행한다.
- **현재 제약:** `_dispatch_all_schedules()`가 활성 (performanceId, scheduleId) 목록을 조회할 방법이 아직 없다 (B의 `performance`/`schedule` 도메인 대기 중). 지금은 `dispatch_once(performance_id, schedule_id)`를 직접 호출하는 것만 가능하며, `tests/test_queue.py`도 이 함수를 직접 호출해 검증한다.

## 우회 플래그

`QUEUE_ENABLED=false`면 `deps.queue.verify_entry_ticket`이 entryTicket 검증 없이 통과시킨다. 대기열이 불안정하거나 미완성일 때 예매 데모를 살리기 위한 유일한 보험이다.
