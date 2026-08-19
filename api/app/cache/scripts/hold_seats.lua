-- [모듈] api/app/cache/scripts/hold_seats.lua
-- [담당] B (인계받아 A가 구현 진행 — 2026-08-19)
-- [역할] 여러 좌석을 한 번에 원자적으로 선점(all-or-nothing). RESV-003(좌석 임시 선점).
--
-- KEYS: seat:lock:{scheduleSeatId} 키 목록 (cache.keys.seat_lock()로 생성, 선점하려는
--       좌석 수만큼 전달). 순서는 seat_ids 순서와 반드시 일치해야 한다.
-- ARGV[1]: hold_id (락의 값으로 저장 — release_seats.lua가 소유자 확인에 사용)
-- ARGV[2]: ttl_seconds (락 TTL, HOLD_TTL_SEC 설정값)
--
-- 반환값:
--   1  -> 전부 성공 (모든 좌석에 락 설정 완료)
--   0  -> 하나 이상 이미 선점/예매된 좌석이 있어 실패 (아무 것도 변경하지 않음)
--
-- [호출자] app.domains.reservation.hold_service.create_hold()
-- [의존] app.cache.client.eval_with_fallback (EVALSHA 실패 시 EVAL 폴백)
--
-- [주의]
-- - 반드시 Valkey master에서만 실행한다 (replica는 read_only라 SET 거부).
-- - 좌석이 이미 예매 확정된 상태(RESERVED)인지 여부는 이 스크립트가 판단하지
--   않는다 — 호출 전 애플리케이션(hold_service)에서 DB의 schedule_seat.status가
--   AVAILABLE인지 먼저 확인한다. 이 스크립트는 "동시에 선점 시도가 몰렸을 때"의
--   원자성만 보장한다 (Valkey 락이 최종 방어선).

local hold_id = ARGV[1]
local ttl = tonumber(ARGV[2])

for i = 1, #KEYS do
    if redis.call("EXISTS", KEYS[i]) == 1 then
        return 0
    end
end

for i = 1, #KEYS do
    redis.call("SET", KEYS[i], hold_id, "EX", ttl)
end

return 1
