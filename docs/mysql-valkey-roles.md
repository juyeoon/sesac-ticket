# MySQL / Valkey 역할 분담

> 코드(`api/app/db/`, `api/app/cache/`, `api/app/domains/reservation/`)를 직접 읽고 정리.
> [`valkey-keys.md`](valkey-keys.md), [`queue-flow.md`](queue-flow.md)와 짝을 이루는 문서 —
> "무슨 키가 있는지/대기열이 어떻게 도는지"가 아니라 "왜 두 저장소로 나눴고 뭘 어디에 둘지"를 정리.

## 왜 나눴나

티켓팅은 오픈 순간 동시에 수백~수천 건이 같은 좌석을 노리는 워크로드다. MySQL 트랜잭션/락만으로
버티려면 커넥션 풀이 순식간에 고갈되고, `SELECT FOR UPDATE` 대기열이 그대로 응답 지연으로 번진다.
그래서 **"지금 이 순간 좌석이 비어있는가"처럼 초 단위로 바뀌고 TTL로 자동 정리돼야 하는 상태는
Valkey가 갖고, "이 회원이 이 공연을 예매했다/취소했다"처럼 영구히 남아야 하는 사실은 MySQL이
갖는다** — 인메모리 락으로 동시성 병목을 흡수하고, 확정된 결과만 RDB에 내려서 감사/정산 근거로
남기는 구조.

## 핵심 원칙

| | MySQL | Valkey |
|---|---|---|
| 역할 | **영속 기록(source of truth)** — 회원/공연/좌석/예매/결제의 최종 상태와 이력 | **실시간 상태 + 락 + 휘발성 데이터** — 지금 이 순간의 점유 상태, 대기열 순번, 세션 |
| 데이터 생명주기 | 영구 (감사·정산·통계 근거) | TTL로 자동 소멸하거나, 재계산 가능한 캐시 |
| 동시성 제어 | 없음(코드상 `SELECT FOR UPDATE` 등 명시적 락 미사용) | Lua 스크립트(`hold_seats.lua`/`release_seats.lua`)로 좌석락 원자적 처리 |
| 장애 시 | DB가 죽으면 예매 자체가 불가 (필수 의존) | Valkey가 죽으면 좌석 잠금이 무력화됨 — 별도 폴백/서킷브레이커 없음 (미해결, 아래 참고) |
| 접근 방식 | ORM(SQLAlchemy) + writer/reader 엔진 분리 | redis-py 클라이언트, master/replica 클라이언트 분리 |

## 읽기/쓰기 분리는 각자 다른 기준으로 나뉜다

두 저장소 모두 "쓰기 전용 vs 읽기 전용" 클라이언트를 분리해두지만 기준이 다르다.

| | MySQL (`db/session.py`) | Valkey (`cache/client.py`) |
|---|---|---|
| 분리 축 | writer / reader (복제 지연 대비) | master / replica (replica가 `read_only`라 쓰기 명령 자체를 거부) |
| 설정값 | `DB_WRITER_URL`, `DB_READER_URL` ([.env.example:6-7](../api/.env.example)) | `VALKEY_MASTER_HOST/PORT`, `VALKEY_REPLICA_HOST/PORT` ([.env.example:12-15](../api/.env.example)) |
| 강제 규칙 | `reservation` 도메인은 **reader를 쓰지 않는다** — reader는 `SELECT FOR UPDATE`가 즉시 에러라서, writer(`get_db`)만 사용 ([model.py:28-29](../api/app/domains/reservation/model.py#L28-L29)) | `ZADD`/`ZPOPMIN`/`EVALSHA` 등 쓰기 계열 명령은 replica에서 거부되므로 **master로만** 호출 |
| 개발 중 예외 | writer/reader가 같은 주소를 가리켜도 무방 (엔진 객체만 분리 생성) | master/replica가 같은 주소를 가리켜도 무방 |

## 좌석 선점(Hold) — 두 저장소가 만나는 지점

콘서트 티켓팅에서 동시성이 가장 몰리는 구간이고, MySQL·Valkey 역할 분담이 실제로 코드에 드러나는
유일한 곳이다. `hold_service.create_hold()` ([hold_service.py:84-141](../api/app/domains/reservation/hold_service.py#L84-L141)) 흐름:

1. **MySQL에서 빠른 실패 체크**: `repository.get_seats_for_hold()`로 좌석이 존재하고
   `status == AVAILABLE`인지 먼저 확인한다. 이건 최종 방어선이 아니라 사전 필터링 — 이미 팔린
   좌석에 대한 락 시도를 미리 걸러내서 Valkey 부하를 줄이는 용도.
2. **Valkey가 최종 원자성을 보장**: `hold_seats.lua`를 `EVALSHA`(SHA 없으면 `EVAL` 폴백,
   `eval_with_fallback()`)로 실행해 요청한 좌석 전부에 대해 all-or-nothing으로 `seat:lock:{scheduleSeatId}`를
   잡는다. 여기서 실패하면(`result != 1`) 이미 MySQL 체크를 통과했어도 `RESV_SEAT_ALREADY_HELD`로 거절 —
   **좌석 점유 여부의 진실은 Valkey 락이고, MySQL의 `AVAILABLE`은 보조 데이터**
   ([model.py:30](../api/app/domains/reservation/model.py#L30)).
3. **성공하면 MySQL에 확정 기록**: `mark_seats_held()`로 `schedule_seat.status`를 `HELD`로,
   `create_seat_hold_log()`로 `seat_hold_log`에 이력을 남긴다. 이 두 MySQL 쓰기는 감사/이력용이며,
   Valkey 락이 이미 걸린 뒤에 일어나므로 실패해도 좌석 잠금 자체는 이미 성립돼 있다.
4. **Valkey에 선점 세션 저장**: `seat:hold:{holdId}`에 JSON(만료 시각 포함)을 `HOLD_TTL_SEC`(기본
   300초, [.env.example:23](../api/.env.example))만큼 저장. `get_hold()`는 이 세션을 우선 조회해서
   DB 왕복 없이 응답한다.
5. **캐시 무효화**: `invalidate_seat_status_cache()`로 `seat:status:{scheduleId}`(TTL 5초,
   `SEAT_STATUS_CACHE_TTL_SEC`)를 지워서 다음 조회가 MySQL 최신 상태로 다시 채워지게 한다.

해제(`release_hold`)/만료(`expire_hold`, `hold_sweeper` 워커가 호출)도 순서만 반대로 같은 원칙을
따른다 — 먼저 Valkey 락을 풀고, 그다음 MySQL 상태를 `AVAILABLE`로 되돌린다.

## 무엇을 어디에 둘지 — 새 기능 추가 시 기준

| 이 데이터는... | 두면 되는 곳 |
|---|---|
| 실패하면 사용자에게 돈/법적 분쟁으로 이어지는 확정 사실 (예매 확정, 결제, 취소) | MySQL |
| 지금 이 순간만 유효하고 TTL 지나면 의미 없어지는 상태 (좌석 임시선점, 대기열 순번, 인증코드) | Valkey |
| 동시에 여러 요청이 경쟁하는 자원에 대한 상호배제 (좌석 락, 워커 리더 선출) | Valkey (Lua 스크립트로 원자적 처리) |
| DB 조회 결과를 잠깐 캐싱해서 부하를 줄이는 용도, DB가 언제든 재생성 가능 | Valkey (짧은 TTL, 무효화 지점 명시) |
| 서비스 재시작/장애 후에도 반드시 살아있어야 하는 값 | MySQL (Valkey는 재시작 시 데이터가 비어있을 수 있다는 전제로 설계) |

## 알아둘 것 / 아직 안 된 것

- **Valkey 장애 시 폴백 없음**: `create_hold()`가 Valkey 호출에 실패(연결 끊김 등)하면 예외가 그대로
  올라가고, MySQL만으로 좌석을 잠그는 대체 경로는 코드에 없다. 좌석 선점 API는 Valkey에 강하게
  의존한다.
- **MySQL 쓰기는 트랜잭션 격리보다 순서에 의존**: `create_hold`/`release_hold`/`expire_hold` 모두
  "Valkey 락 조작 성공 → MySQL 커밋"의 순서를 지키지만, 그 사이에 프로세스가 죽으면 Valkey 락은
  잡혀 있는데 MySQL은 `AVAILABLE`로 남는 등의 불일치가 생길 수 있다 — 현재는 `hold_sweeper`
  워커가 TTL 만료 기준으로 정리하는 것으로 완화(정합성 보장 로직은 아님).
  - 관련: 대기열 도메인 `WAITING → READY → ENTERED/EXPIRED` 상태 전이도 대기열 모듈과 예매
    도메인에 걸쳐 있어 비슷한 성격의 이슈가 있다 ([queue-flow.md](queue-flow.md) 참고).
- **결제(PG) 관련 캐시는 아직 코드에 없음** — 무통장입금(`BANK_TRANSFER_PAYMENT_DUE_HOURS`)만
  구현돼 있고, 이 흐름은 MySQL만 사용한다(Valkey 개입 없음).

## 참고

- [valkey-keys.md](valkey-keys.md) — Valkey 키 이름/TTL/read·write 지점 상세
- [queue-flow.md](queue-flow.md) — 대기열이 Valkey만 쓰고 MySQL을 아예 안 쓰는 이유
- [../docs/OWNERSHIP.md](../docs/OWNERSHIP.md) — 이 문서와는 별개로, "누가(A/B) 어떤 파일을
  담당하는지"의 코드 오너십 분담표
