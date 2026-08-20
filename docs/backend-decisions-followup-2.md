# 백엔드와 맞춰야 할 것들 — 3차 (실 API 연동 중 발견)

> [`backend-decisions-needed.md`](./backend-decisions-needed.md)(1차)와 [`backend-decisions-followup-1.md`](./backend-decisions-followup-1.md)(2차)는 이미 공유드려서 답변받은 문서라 그대로 두고, 이번에 프론트를 mock에서 실 API로 완전히 전환하면서 새로 발견한 것만 이 문서로 따로 드립니다.

## 🔴 확인 필요 — 대기열 dispatcher가 로컬에서 동작하지 않음

로컬에 `api/api`를 그대로 띄워서(Docker MySQL + Valkey, `uv sync`, `.env.example` 기준 설정) 연동 테스트를 하다가, **`queue_dispatcher` 워커가 대기 인원을 한 명도 방출하지 못하는 문제**를 발견했습니다.

**재현 환경**: Valkey는 `valkey/valkey:7`(Docker Hub, valkey 7.2.14 / redis_version 7.2.4 자체 보고값) 컨테이너, Python 패키지는 리포에 커밋된 `uv.lock` 그대로(`redis==8.1.0`).

**증상**: `app/workers/queue_dispatcher.py`의 `dispatch_once()`가 호출하는 `client.zpopmin(key, count)`에서 아래 에러가 남:
```
redis.exceptions.ResponseError: unknown command 'ZPOPMIN'
```

**직접 재현/격리한 내용**:
- 같은 Valkey 컨테이너에 `valkey-cli`로 직접 `ZADD`/`ZPOPMIN`을 치면 정상 동작합니다 (서버 자체 문제 아님).
- 같은 Python 프로세스, 같은 커넥션에서 `PING`/`SET`/`GET`/`ZADD`/`ZRANGE`는 전부 정상 동작하고, **`ZPOPMIN`만** 실패합니다.
- `app/cache/client.py`에 명시된 `protocol=2`를 빼고 연결하면 이번엔 `HELLO` 자체가 `unknown command`로 실패합니다(주석에 적힌 "오래된 서버 호환용 RESP2 강제"의 반대 증상) — 즉 `protocol=2`를 켜야 커넥션 자체는 정상인데, 그 상태에서 `ZPOPMIN`만 깨지는 상황입니다.
- 재현 스크립트:
  ```python
  import redis
  c = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True, protocol=2)
  c.zadd("z", {"a": 1})
  c.zpopmin("z", 1)  # ResponseError: unknown command 'ZPOPMIN'
  ```

이 명령이 막히면 `queue_dispatcher`가 항상 빈 배치를 방출하는 걸로 끝나서, 대기열에 들어간 사용자가 영원히 `WAITING`에 머물고 좌석 선택 화면까지 못 넘어갑니다. 프론트 쪽에서 고칠 수 있는 부분이 아니라 백엔드팀 확인 부탁드립니다. 배포 서버(`43.201.61.179:8000`)는 이번엔 접속이 안 돼서 거기서도 재현되는지는 확인 못 했습니다 — 혹시 배포 환경은 다른 Valkey/redis-py 조합이라 문제가 없는 상태라면, 그 조합이 뭔지 알려주시면 로컬도 맞추겠습니다.

## 🟡 확인 요청 — 회원가입 시 이메일 인증 순서

`POST /auth/email/verify-request`를 코드로 확인해보니, 이미 가입된 회원(`member_repository.get_member_by_email`로 조회됨)에게만 인증 코드를 발급하고, 없는 이메일이면 조용히 무시하고 `{sent:true}`만 응답하도록 돼 있었습니다(`auth/service.py:150-153`). 그리고 `POST /auth/signup`과 `login` 둘 다 이메일 인증 여부(`email_verified`)를 확인하지 않습니다.

- 이 말은 **"가입 전에 이메일 인증부터 받는" 흐름 자체가 지금 API로는 불가능**하다는 뜻이라, 프론트 회원가입 화면에서 이메일 인증 단계를 아예 제거했습니다 (이메일/닉네임/비밀번호만 받고 바로 `signup` 호출).
- 이게 의도하신 설계가 맞는지 확인 부탁드립니다. 저희가 이해한 바로는: 이메일 인증은 회원가입 게이트가 아니라 **가입 후 별도의 "본인 확인" 기능**(실제로 마이페이지 정보수정 API가 이 코드를 재사용하고 있는 것도 확인함)인 것 같은데, 맞다면 지금 프론트 대응이 맞습니다. 혹시 "가입 후 이메일 인증을 유도하는 화면"이 따로 필요하다고 생각하신 거라면(예: 인증 안 하면 일부 기능 제한 등) 알려주시면 화면을 추가하겠습니다.

## 🟢 참고만 하시면 되는 것 (프론트에서 이미 대응 완료)

이번에 `/openapi.json`을 직접 떠서 확인한 것들 — 답변 필요 없고, 혹시 의도와 다르게 응답이 나가고 있다면만 알려주세요.

| 항목 | 확인된 값 | 프론트 대응 |
|---|---|---|
| `GET /users/me/favorites` | `{content: [{performanceId, title, thumbnailUrl}], totalElements}` | ID 배열이라고 가정했던 걸 수정, 공연 목록과 교차조회하던 로직 제거 |
| `GET /reservations/bank-transfer/{id}`의 좌석 항목 | `{section, row, number, grade, price}` — `seatId` 없음 | key를 seatId 대신 배열 index로 사용 |
| 위 응답 전체 | `depositorName` 필드 없음 | 화면에서 입금자명 표시 제거 |
| `GET /performances/{id}/schedules` | `{id, startAt, saleStatus}` — 가격/등급 정보 없음 | 대신 공연 상세(`GET /performances/{id}`)의 `schedules` 필드(가격 포함) 사용, 별도 API 호출 제거 |
| 공유 링크 발급 API | 존재하지 않음 | 클라이언트에서 현재 페이지 URL을 그대로 공유하도록 변경 |
| 좌석 `row` | 문자열(`"1"`) | 숫자로 가정했던 타입 수정 |
| `MAX_SEATS_PER_HOLD` | `2` | 프론트 좌석 선택 최대 개수를 4 → 2로 수정 |
| 좌석 상태 | `AVAILABLE`/`HELD`/`RESERVED`만 존재 | mock에 있던 `SOLD` 제거(2차 문서에서 이미 답변받은 내용, 최종 코드 반영 완료) |
