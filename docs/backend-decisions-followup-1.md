# 백엔드와 맞춰야 할 것들 — 2차 (실제 서버 확인 후)

> [`backend-decisions-needed.md`](./backend-decisions-needed.md)를 공유드린 뒤, 실제 배포 서버(`43.201.61.179:8000/docs`)와 `feature/integration2`의 `api/.env.example`을 직접 까봐서 새로 확인/추가된 내용만 정리한 후속 문서입니다. **원본 파일은 그대로 두고 이 파일로 따로 드립니다.**

## ✅ 확인 완료 (실제 서버/코드로 검증함, 2026-08-20)

원본 문서의 질문 중 아래는 실제 서버·코드 확인으로 답이 나왔습니다 — 답장 안 주셔도 됩니다.

| 원본 항목 | 확인된 값 |
|---|---|
| 6. 좌석 선택 최대 개수 제한 | `.env.example`에 관련 항목 없음 → 서버 쪽엔 아직 제한 없는 것으로 보임 (여전히 확인은 필요) |
| 7. 입금 기한 | `BANK_TRANSFER_PAYMENT_DUE_HOURS=24` — 프론트 mock이 이미 24시간으로 가정한 것과 일치 |
| 8. 무통장입금 계좌 정보 | **문자열 하나**(`BANK_ACCOUNT_INFO` 환경변수)로 확인 — 객체 아님. 프론트 코드 수정 완료 |
| (신규) Hold TTL | `HOLD_TTL_SEC=300`(5분) — 프론트 mock과 일치 |
| (신규) 대기열 폴링 주기 | `QUEUE_POLL_INTERVAL_SEC=3` — 프론트가 이미 3초로 구현한 것과 일치 |
| (신규) 대기열 우회 플래그 | `QUEUE_ENABLED` 실제로 존재 (true/false) — 2번 항목 방향 확인됨 |
| 11. 관심 공연(즐겨찾기) | 실제로 구현되는 중 확인(`FavoriteItem`/`FavoritedResponse` 등 스키마 실제 존재) — 프론트 하트 버튼 계속 유지하기로 함 |
| (신규) 회원가입 gender/ageRange | 실제로 존재, 둘 다 optional (`required`는 email/password/nickname뿐) |
| (신규) 공연 목록의 `category`/`venue` | `category`는 `{id, name}` 객체, `venue`는 `{id, name, address}`(목록에도 주소 포함) — 프론트가 문자열/부분 객체로 잘못 가정했던 것 발견, 수정 완료 |
| (신규) 공연 상세의 `status` | **필드 자체가 없음** (목록 조회에만 있음) — 프론트가 상세 화면 배지 조건부 렌더링으로 수정 |
| (신규) 좌석 등급 라벨 | 접미사 없는 `VIP`/`R`/`S` (프론트 mock의 "R석"류와 다름 — 실제 시드 데이터 기준) |
| (신규) 카테고리 종류 | 시드 데이터엔 콘서트/뮤지컬 2개뿐 (프론트 mock엔 데모용으로 연극/전시 2개를 더 추가해둔 상태 — 실제 연동 시 정리 예정) |
| 5. 좌석 좌표(x, y) | 확인됨 — 구역별 x 오프셋 + 좌석번호×20, 행번호×20 형태의 평면 그리드 좌표. **다만 스키마상 x/y가 nullable**이라 값이 없을 가능성은 여전히 고려 필요 |
| (신규) 에러 응답 형식 | `{"errorCode": "...", "message": "..."}` — 프론트 mock과 이미 동일한 형식으로 확인됨 |
| (신규) 공연 목록 `status` 값 | 실제 시드 데이터는 전부 `"ACTIVE"` (프론트 mock의 UPCOMING/ON_SALE/CLOSED와 다름 — 다른 상태값이 실제로 뭐가 있는지는 아직 확인 못 함, 계속 열어둠) |

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

ALB → nginx → gunicorn 프록시 체인이 클라이언트 IP를 제대로 전달하는지 화면에서 바로 확인하려는 용도입니다(`ProxyHeadersMiddleware`가 이미 처리 중인 값을 그대로 응답에 얹기만 하면 됨). 프론트는 이 형태를 가정하고 footer에 먼저 붙여뒀습니다: `Front v0.1.0 · Server v1.0.0-mock (api-a · ap-northeast-2a) · X-Forwarded-For: ...`

**1번(회차→공연 역참조 API 없음)**: 실제 서버에도 여전히 없는 것 확인했습니다 — 원본 질문 그대로 유효합니다.

**3번(Hold 이후 좌석 상태값)**: `ConfirmReservationResponse` 스키마가 실제로 존재하는 걸 보면 예매 확정 처리 자체는 있는 것 같은데, 그 사이 좌석 상태 이름이 뭔지는 여전히 궁금합니다. `docs/seat-state-machine.md` 나오면 알려주세요.

**9번(entryTicket 유효시간)**: `QUEUE_TOKEN_TTL_SEC=1800`(30분)은 확인했는데, 이게 `queueToken` TTL인지 `entryTicket` TTL인지 명확하지 않습니다. 프론트는 entryTicket을 세션스토리지에 9분간 캐시 중 — 실제 TTL과 크게 다르면 좌석 선점 시점에 403이 날 수 있어서 여쭤봅니다.
