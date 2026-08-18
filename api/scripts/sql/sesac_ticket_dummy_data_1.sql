-- =====================================================================
-- 새싹티켓 핵심 예매 흐름(좌석 선점 → 예매 → 결제 → 확정/취소) 테스트용 더미 데이터
-- 대상 시나리오 3가지 (공연/회차/좌석 1세트를 공유하고, 회원 3명이 각각 다른 상태를 대표)
--
--   시나리오 1 (member_id=1) : 정상 완료   - 선점 → 예매(PENDING) → 입금확인 → CONFIRMED
--   시나리오 2 (member_id=2) : 결제 대기중 - 선점 → 예매(PENDING) 생성 후 아직 미확정 (좌석 HELD 유지)
--   시나리오 3 (member_id=3) : 결제 시간초과로 취소 - 선점 → 예매(PENDING) → 입금기한 경과 → CANCELLED, 좌석 AVAILABLE로 반환
--
-- 이 3가지만으로 챌린지 포인트인 "좌석 점유 ↔ 예매 ↔ 결제 사이의 정합성"과
-- "취소 시 좌석이 실제로 반환되어 재예매 가능한 상태가 되는지"를 검증할 수 있습니다.
--
-- [수정 2026-08-18] password_hash를 자릿수만 맞춘 가짜 문자열(dummy...)에서
-- 실제 bcrypt 해시로 교체함 (원본은 bcrypt.checkpw()에 넣으면 "Invalid salt"로
-- 에러가 나서 로그인 테스트가 불가능했음). 아래 4개 계정 전부 평문 비밀번호는
-- "test1234!" 로 통일. B도 동일 파일을 갖고 있다면 이 변경사항을 공유할 것.
-- =====================================================================

-- 1) 기준 데이터 (카테고리 / 공연장 / 관리자)
INSERT INTO `category` (`id`, `name`, `sort_order`, `created_at`) VALUES
  (1, '콘서트', 1, '2026-08-01 09:00:00');

INSERT INTO `venue` (`id`, `name`, `address`) VALUES
  (1, '새싹 아레나', '서울시 강남구 새싹로 123');

-- 평문 비밀번호: test1234!
INSERT INTO `admin` (`id`, `admin_id`, `password_hash`, `name`, `role`, `created_at`) VALUES
  (1, 'admin01', '$2b$12$Y4XglY6/YEbOCZjmhIArZ.f3V0p9.adqGfkFxR7M28yEp1prZZKK.', '운영관리자', 'SUPER', '2026-08-01 09:00:00');

-- 2) 좌석 (공연장 좌석 원본 3석: VIP 2석 + R석 1석)
INSERT INTO `venue_seat` (`id`, `venue_id`, `section`, `row_no`, `seat_no`, `x`, `y`, `grade`) VALUES
  (1, 1, 'A', '1', 1, 10, 10, 'VIP'),
  (2, 1, 'A', '1', 2, 20, 10, 'VIP'),
  (3, 1, 'B', '1', 1, 10, 50, 'R');

-- 3) 공연 / 좌석 등급별 가격
INSERT INTO `performance` (`id`, `title`, `category_id`, `description`, `venue_id`, `ticket_open_at`, `ticket_close_at`, `running_time_min`, `age_limit`, `status`, `created_at`, `updated_at`) VALUES
  (1, '새싹 콘서트 2026', 1, '2026 새싹티켓 테스트용 공연', 1, '2026-08-01 10:00:00', '2026-08-31 23:59:59', 120, '12세 이상', 'ACTIVE', '2026-08-01 09:30:00', NULL);

INSERT INTO `performance_seat_grade` (`id`, `performance_id`, `grade`, `price`) VALUES
  (1, 1, 'VIP', 150000),
  (2, 1, 'R', 100000);

-- 4) 회차 (하나의 회차에 3석 모두 배치)
INSERT INTO `schedule` (`id`, `performance_id`, `perf_date`, `perf_time`, `status`, `created_at`) VALUES
  (1, 1, '2026-09-01', '19:00:00', 'OPEN', '2026-08-01 09:30:00');

-- 회차별 좌석 상태
--   seat 1 (VIP) -> 시나리오1 완료로 RESERVED
--   seat 2 (VIP) -> 시나리오2 결제대기로 HELD
--   seat 3 (R)   -> 시나리오3 취소로 좌석 반환되어 AVAILABLE
INSERT INTO `schedule_seat` (`id`, `schedule_id`, `venue_seat_id`, `grade`, `price`, `status`) VALUES
  (1, 1, 1, 'VIP', 150000, 'RESERVED'),
  (2, 1, 2, 'VIP', 150000, 'HELD'),
  (3, 1, 3, 'R',   100000, 'AVAILABLE');

-- 5) 회원 3명 (각 시나리오 담당) — 평문 비밀번호 전부 동일: test1234!
INSERT INTO `member` (`id`, `email`, `password_hash`, `nickname`, `gender`, `age_range`, `status`, `email_verified`, `withdrawn_at`, `created_at`) VALUES
  (1, 'member1@test.com', '$2b$12$272DPWEhVPPELbnY.S.Rdugtl4s/DHnGWESByqXLC5BGRWja3128C', '다란', 'F', '20대', 'ACTIVE', true, NULL, '2026-08-10 12:00:00'),
  (2, 'member2@test.com', '$2b$12$5Ye2GMD8PXeWc0g1xotzvuxsKxZRPc/STBlLTMi5eHnYJ7OKOBmca', '현지', 'F', '20대', 'ACTIVE', true, NULL, '2026-08-11 12:00:00'),
  (3, 'member3@test.com', '$2b$12$oStGiGa.we4h7rPFZnmpDu40AmsQrngbF3WVWWCNx3rzuXcF1AT12', '주연', 'M', '20대', 'ACTIVE', true, NULL, '2026-08-12 12:00:00');

-- 6) 좌석 선점 로그 (Valkey holdId와 매핑되는 값이므로 실제 서비스라면 Redis에도 동일 holdId로 키가 존재해야 함)
--   시나리오1,2 : 예매로 전환 완료 -> CONVERTED
--   시나리오3   : 예매 생성까지는 전환됐지만 이후 결제 타임아웃으로 좌석 반환 -> 로그 자체는 CONVERTED로 남기고
--                 반환 사실은 reservation.status = CANCELLED 로 표현 (원본 선점 이력은 보존)
INSERT INTO `seat_hold_log` (`id`, `hold_id`, `member_id`, `schedule_id`, `schedule_seat_ids`, `status`, `expires_at`, `released_at`, `created_at`) VALUES
  (1, 'HOLD-20260818-0001', 1, 1, JSON_ARRAY(1), 'CONVERTED', '2026-08-18 10:05:00', NULL,                  '2026-08-18 10:00:00'),
  (2, 'HOLD-20260818-0002', 2, 1, JSON_ARRAY(2), 'CONVERTED', '2026-08-18 11:05:00', NULL,                  '2026-08-18 11:00:00'),
  (3, 'HOLD-20260818-0003', 3, 1, JSON_ARRAY(3), 'CONVERTED', '2026-08-18 09:05:00', '2026-08-18 09:40:00', '2026-08-18 09:00:00');

-- 7) 예매
--   시나리오1 : CONFIRMED (입금 확인 완료)
--   시나리오2 : PENDING_PAYMENT (아직 입금 확인 전, 입금기한 이전)
--   시나리오3 : CANCELLED (입금기한 경과로 취소)
INSERT INTO `reservation` (`id`, `member_id`, `schedule_id`, `hold_id`, `payment_method`, `status`, `total_amount`, `created_at`, `confirmed_at`, `cancelled_at`) VALUES
  (1, 1, 1, 'HOLD-20260818-0001', 'BANK_TRANSFER', 'CONFIRMED',       150000, '2026-08-18 10:00:30', '2026-08-18 10:30:00', NULL),
  (2, 2, 1, 'HOLD-20260818-0002', 'BANK_TRANSFER', 'PENDING_PAYMENT', 150000, '2026-08-18 11:00:30', NULL,                  NULL),
  (3, 3, 1, 'HOLD-20260818-0003', 'BANK_TRANSFER', 'CANCELLED',      100000, '2026-08-18 09:00:30', NULL,                  '2026-08-18 09:40:00');

-- 8) 예매-좌석 매핑 (예매 시점 가격 스냅샷)
INSERT INTO `reservation_seat` (`id`, `reservation_id`, `schedule_seat_id`, `price_snapshot`) VALUES
  (1, 1, 1, 150000),
  (2, 2, 2, 150000),
  (3, 3, 3, 100000);

-- 9) 무통장입금 결제 정보
--   시나리오1 : 관리자가 입금 확인 후 확정 처리(confirmed_by_admin_id, confirmed_at 존재)
--   시나리오2 : 입금기한이 아직 남아있고 확인 전
--   시나리오3 : 입금기한이 지나도록 미입금 -> 이후 배치/스케줄러가 CANCELLED 처리했다고 가정
INSERT INTO `bank_transfer_payment` (`id`, `reservation_id`, `depositor_name`, `bank_account_info`, `payment_due_at`, `confirmed_by_admin_id`, `confirmed_at`) VALUES
  (1, 1, '신다란', '신한은행 110-123-456789 (새싹티켓)', '2026-08-18 12:00:00', 1,    '2026-08-18 10:30:00'),
  (2, 2, '안현지', '신한은행 110-123-456789 (새싹티켓)', '2026-08-18 13:00:00', NULL, NULL),
  (3, 3, '박주연', '신한은행 110-123-456789 (새싹티켓)', '2026-08-18 09:30:00', NULL, NULL);
