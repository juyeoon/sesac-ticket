## 추가로 여쭤볼 것

**4번(Front/Server 버전 노출) 항목에 필드 하나만 추가 요청**드립니다 — 원래 제안한 응답에 `clientIp`(X-Forwarded-For 값)를 추가해주실 수 있을까요?

```
GET /api/v1/version
{
  "apiVersion": "1.0.0",
  "app": { ... 기존 그대로 ... },
  "server": { "instanceId": "api-a", "az": "ap-northeast-2a" },
  "clientIp": "<요청의 X-Forwarded-For 헤더 값 그대로>"
}
```

> 프론트 제안 그대로 수용
>
> ```jsx
> GET /api/v1/version
> {
> "apiVersion": "1.0.0",
> "app": { "latestVersion": "...", "minRequiredVersion": "...", "forceUpdate": false, "updateUrl": "..." },
> "server": { "instanceId": "api-a", "az": "ap-northeast-2a" },
> "clientIp": "1.2.3.4"
> }
> ```

ALB → nginx → gunicorn 프록시 체인이 클라이언트 IP를 제대로 전달하는지 화면에서 바로 확인하려는 용도입니다(`ProxyHeadersMiddleware`가 이미 처리 중인 값을 그대로 응답에 얹기만 하면 됨). 프론트는 이 형태를 가정하고 footer에 먼저 붙여뒀습니다: `Front v0.1.0 · Server v1.0.0-mock (api-a · ap-northeast-2a) · X-Forwarded-For: ...`

**3번(Hold 이후 좌석 상태값)**: `ConfirmReservationResponse` 스키마가 실제로 존재하는 걸 보면 예매 확정 처리 자체는 있는 것 같은데, 그 사이 좌석 상태 이름이 뭔지는 여전히 궁금합니다. `docs/seat-state-machine.md` 나오면 알려주세요.

> **좌석 레벨** 상태(`schedule_seat.status`, `GET /schedules/{scheduleId}/seats` 응답의 `status`): `AVAILABLE` → `HELD`(선점) → `RESERVED`(예매 생성). **`SOLD`라는 상태는 존재하지 않음.**

> **예매 레벨** 상태(`reservation.status`, `ConfirmReservationResponse.status`/`GET /reservations/bank-transfer/{id}`의 `status`로 노출): `PENDING_PAYMENT` → `CONFIRMED` / `CANCELLED` / `EXPIRED`. 코드로 확인함 — `ConfirmReservationResponse` 스키마 실제로 존재하고 이미 구현·테스트 완료된 상태 맞습니다.

> 즉 "입금대기중 vs 확정"을 화면에서 구분하려면 **좌석 상태(`RESERVED`)만으로는 부족하고, 예매 상세 API의 `status`를 반드시 같이 조회**해야 함.

**9번(entryTicket 유효시간)**: `QUEUE_TOKEN_TTL_SEC=1800`(30분)은 확인했는데, 이게 `queueToken` TTL인지 `entryTicket` TTL인지 명확하지 않습니다. 프론트는 entryTicket을 세션스토리지에 9분간 캐시 중 — 실제 TTL과 크게 다르면 좌석 선점 시점에 403이 날 수 있어서 여쭤봅니다.

> `QUEUE_TOKEN_TTL_SEC=1800`(30분)은 **queueToken**(대기열 안에서 순번 기다리는 토큰) 전용 TTL입니다 — 이 안에 dispatcher가 방출을 못 시키면 대기열 진입 자체가 만료됩니다. **entryTicket**(대기열 통과 후 실제 좌석 선점에 쓰는 토큰)의 TTL은 이것과 완전히 별개입니다.

> 코드로 확인: `workers/queue_dispatcher.py`의 `_ENTRY_TICKET_TTL_SEC = 300`(5분)으로 **하드코딩**돼 있고, `.env`/`config.py`에는 노출되지 않는 값입니다 — 그래서 프론트에서 확인하기 어려웠을 것 같습니다.
