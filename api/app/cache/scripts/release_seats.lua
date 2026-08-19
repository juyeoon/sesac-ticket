-- [모듈] api/app/cache/scripts/release_seats.lua
-- [담당] B (인계받아 A가 구현 진행 — 2026-08-19)
-- [역할] 선점된 좌석 해제. RESV-012(좌석 선점 해제) + hold_sweeper의 만료 정리에도 사용.
--
-- KEYS: seat:lock:{scheduleSeatId} 키 목록 (해제하려는 좌석)
-- ARGV[1]: hold_id (본인 소유의 락일 때만 해제되도록 검증)
--
-- 반환값: 실제로 삭제된 락 개수 (0이면 이미 만료됐거나 본인 소유가 아니었다는 뜻).
--
-- [호출자]
-- - app.domains.reservation.hold_service.release_hold() (RESV-012, 사용자 명시적 해제)
-- - app.workers.hold_sweeper (TTL 만료분 정리 — 이 경우 이미 Valkey TTL로 자동
--   삭제됐을 수 있으므로, hold_sweeper는 주로 DB(seat_hold_log/schedule_seat) 상태
--   동기화가 목적이고 이 스크립트는 방어적으로 한 번 더 정리하는 용도)
--
-- [주의]
-- - 반드시 Valkey master에서만 실행한다.
-- - 값이 hold_id와 다른 키는 절대 건드리지 않는다 (다른 사람이 이미 새로
--   선점했거나, 애초에 본인 것이 아닌 경우 보호).

local hold_id = ARGV[1]
local released = 0

for i = 1, #KEYS do
    local current = redis.call("GET", KEYS[i])
    if current == hold_id then
        redis.call("DEL", KEYS[i])
        released = released + 1
    end
end

return released
