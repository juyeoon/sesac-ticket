-- =====================================================================
-- 새싹티켓 (sesac ticket) DB 초기화 스크립트 (init.sql)
--
-- 목적 : 로컬 개발 환경 최초 구축 시, 전체 테이블/인덱스/제약조건을
--        한 번에 생성하기 위한 스크립트입니다. (더미 데이터 X, 스키마만)
-- 기준 : dbdiagram.io "sesac-ticket" ERD export본 (2026-08-18, FK 방향 수정본) 기준
-- 실행 : mysql -uroot -p < sesac_ticket_init.sql
-- 이후 : 마이그레이션 도구(Flyway/Liquibase)를 도입하게 되면
--        이 파일을 V1__init_schema.sql 로 그대로 사용할 수 있습니다.
-- =====================================================================

CREATE DATABASE IF NOT EXISTS `sesac_ticket`
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE `sesac_ticket`;

-- =====================================================================
-- 1. 회원 / 관리자
-- =====================================================================

CREATE TABLE `member` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `email` varchar(255) UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `nickname` varchar(255) NOT NULL,
  `gender` varchar(255),
  `age_range` varchar(255),
  `status` varchar(255) NOT NULL COMMENT 'ACTIVE, WITHDRAWN',
  `email_verified` boolean NOT NULL DEFAULT false,
  `withdrawn_at` datetime,
  `created_at` datetime NOT NULL DEFAULT (now())
);

CREATE TABLE `admin` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `admin_id` varchar(255) UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now())
);

-- =====================================================================
-- 2. 공연 마스터 데이터 (카테고리 / 공연장 / 좌석 / 공연 / 이미지 / 등급)
-- =====================================================================

CREATE TABLE `category` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) UNIQUE NOT NULL,
  `sort_order` int NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT (now())
);

CREATE TABLE `venue` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `address` varchar(255)
);

CREATE TABLE `venue_seat` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `venue_id` bigint NOT NULL,
  `section` varchar(255) NOT NULL,
  `row_no` varchar(255) NOT NULL,
  `seat_no` int NOT NULL,
  `x` int,
  `y` int,
  `grade` varchar(255) NOT NULL
);

CREATE TABLE `performance` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `category_id` bigint NOT NULL,
  `description` text,
  `venue_id` bigint NOT NULL,
  `ticket_open_at` datetime,
  `ticket_close_at` datetime,
  `running_time_min` int,
  `age_limit` varchar(255),
  `status` varchar(255) NOT NULL COMMENT 'ACTIVE, HIDDEN, ENDED',
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime
);

CREATE TABLE `performance_image` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `performance_id` bigint NOT NULL,
  `file_key` varchar(255) NOT NULL,
  `sort_order` int NOT NULL DEFAULT 0
);

CREATE TABLE `performance_seat_grade` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `performance_id` bigint NOT NULL,
  `grade` varchar(255) NOT NULL,
  `price` int NOT NULL
);

-- =====================================================================
-- 3. 회차 / 회차별 좌석 상태
-- =====================================================================

CREATE TABLE `schedule` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `performance_id` bigint NOT NULL,
  `perf_date` date NOT NULL,
  `perf_time` time NOT NULL,
  `status` varchar(255) NOT NULL COMMENT 'OPEN, CLOSED',
  `created_at` datetime NOT NULL DEFAULT (now())
);

CREATE TABLE `schedule_seat` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `schedule_id` bigint NOT NULL,
  `venue_seat_id` bigint NOT NULL,
  `grade` varchar(255) NOT NULL,
  `price` int NOT NULL,
  `status` varchar(255) NOT NULL COMMENT 'AVAILABLE, HELD, RESERVED'
);

-- =====================================================================
-- 4. 예매 핵심 흐름 (좌석 선점 -> 예매 -> 결제)
--    챌린지 포인트: 동시성 / 트랜잭션 정합성이 집중되는 구간
-- =====================================================================

CREATE TABLE `seat_hold_log` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `hold_id` varchar(255) UNIQUE NOT NULL COMMENT 'Valkey holdId와 매핑',
  `member_id` bigint NOT NULL,
  `schedule_id` bigint NOT NULL,
  `schedule_seat_ids` json NOT NULL COMMENT '선점에 포함된 schedule_seat.id 배열',
  `status` varchar(255) NOT NULL COMMENT 'HOLDING, RELEASED, EXPIRED, CONVERTED',
  `expires_at` datetime NOT NULL,
  `released_at` datetime,
  `created_at` datetime NOT NULL DEFAULT (now())
);

CREATE TABLE `reservation` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `member_id` bigint NOT NULL,
  `schedule_id` bigint NOT NULL,
  `hold_id` varchar(255) UNIQUE NOT NULL COMMENT 'seat_hold_log.hold_id 참조 - 출처 추적 및 중복생성 방지',
  `payment_method` varchar(255) NOT NULL COMMENT 'BANK_TRANSFER, PG',
  `status` varchar(255) NOT NULL COMMENT 'PENDING_PAYMENT, CONFIRMED, CANCELLED, EXPIRED',
  `total_amount` int NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `confirmed_at` datetime,
  `cancelled_at` datetime
);

CREATE TABLE `reservation_seat` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `reservation_id` bigint NOT NULL,
  `schedule_seat_id` bigint NOT NULL,
  `price_snapshot` int NOT NULL
);

CREATE TABLE `bank_transfer_payment` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `reservation_id` bigint UNIQUE NOT NULL,
  `depositor_name` varchar(255) NOT NULL,
  `bank_account_info` varchar(255) NOT NULL,
  `payment_due_at` datetime NOT NULL,
  `confirmed_by_admin_id` bigint,
  `confirmed_at` datetime
);

CREATE TABLE `pg_payment` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `reservation_id` bigint UNIQUE NOT NULL,
  `pg_provider` varchar(255),
  `pg_transaction_id` varchar(255),
  `pg_status` varchar(255),
  `raw_payload` json,
  `confirmed_at` datetime
);

-- =====================================================================
-- 5. 부가 기능 (관심 공연 / 고객센터 / 앱 버전)
-- =====================================================================

CREATE TABLE `member_favorite` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `member_id` bigint NOT NULL,
  `performance_id` bigint NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now())
);

CREATE TABLE `support_post` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `content` text NOT NULL,
  `category` varchar(255),
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime
);

CREATE TABLE `app_version` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `platform` varchar(255) NOT NULL COMMENT 'ios, android, web',
  `api_version` varchar(255) NOT NULL,
  `latest_version` varchar(255) NOT NULL,
  `min_required_version` varchar(255) NOT NULL,
  `force_update` boolean NOT NULL DEFAULT false,
  `update_url` varchar(255)
);

-- =====================================================================
-- 6. 유니크 인덱스 (동시성/중복 방지와 직결되는 제약)
-- =====================================================================

-- 회원 1명당 같은 공연을 관심등록 2번 못 하게 방지
CREATE UNIQUE INDEX `member_favorite_index_0` ON `member_favorite` (`member_id`, `performance_id`);

-- 같은 공연장에 동일 구역/열/번호의 좌석이 중복 등록되지 않게 방지
CREATE UNIQUE INDEX `venue_seat_index_1` ON `venue_seat` (`venue_id`, `section`, `row_no`, `seat_no`);

-- 공연 1개당 같은 등급이 중복 정의되지 않게 방지
CREATE UNIQUE INDEX `performance_seat_grade_index_2` ON `performance_seat_grade` (`performance_id`, `grade`);

-- 같은 회차에 같은 좌석이 중복 배치되지 않게 방지 (좌석 중복 판매 방지의 1차 방어선)
CREATE UNIQUE INDEX `schedule_seat_index_3` ON `schedule_seat` (`schedule_id`, `venue_seat_id`);

-- 같은 예매 안에 같은 좌석이 중복으로 담기지 않게 방지
CREATE UNIQUE INDEX `reservation_seat_index_4` ON `reservation_seat` (`reservation_id`, `schedule_seat_id`);

-- =====================================================================
-- 7. 외래키(FK) 제약
-- =====================================================================

ALTER TABLE `member_favorite` ADD FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);
ALTER TABLE `member_favorite` ADD FOREIGN KEY (`performance_id`) REFERENCES `performance` (`id`);

ALTER TABLE `performance` ADD FOREIGN KEY (`category_id`) REFERENCES `category` (`id`);
ALTER TABLE `performance` ADD FOREIGN KEY (`venue_id`) REFERENCES `venue` (`id`);

ALTER TABLE `venue_seat` ADD FOREIGN KEY (`venue_id`) REFERENCES `venue` (`id`);

ALTER TABLE `performance_image` ADD FOREIGN KEY (`performance_id`) REFERENCES `performance` (`id`);

ALTER TABLE `performance_seat_grade` ADD FOREIGN KEY (`performance_id`) REFERENCES `performance` (`id`);

ALTER TABLE `schedule` ADD FOREIGN KEY (`performance_id`) REFERENCES `performance` (`id`);

ALTER TABLE `schedule_seat` ADD FOREIGN KEY (`schedule_id`) REFERENCES `schedule` (`id`);
ALTER TABLE `schedule_seat` ADD FOREIGN KEY (`venue_seat_id`) REFERENCES `venue_seat` (`id`);

ALTER TABLE `seat_hold_log` ADD FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);
ALTER TABLE `seat_hold_log` ADD FOREIGN KEY (`schedule_id`) REFERENCES `schedule` (`id`);

ALTER TABLE `reservation` ADD FOREIGN KEY (`member_id`) REFERENCES `member` (`id`);
ALTER TABLE `reservation` ADD FOREIGN KEY (`schedule_id`) REFERENCES `schedule` (`id`);
ALTER TABLE `reservation` ADD FOREIGN KEY (`hold_id`) REFERENCES `seat_hold_log` (`hold_id`);

ALTER TABLE `reservation_seat` ADD FOREIGN KEY (`reservation_id`) REFERENCES `reservation` (`id`);
ALTER TABLE `reservation_seat` ADD FOREIGN KEY (`schedule_seat_id`) REFERENCES `schedule_seat` (`id`);

ALTER TABLE `bank_transfer_payment` ADD FOREIGN KEY (`reservation_id`) REFERENCES `reservation` (`id`);
ALTER TABLE `bank_transfer_payment` ADD FOREIGN KEY (`confirmed_by_admin_id`) REFERENCES `admin` (`id`);

ALTER TABLE `pg_payment` ADD FOREIGN KEY (`reservation_id`) REFERENCES `reservation` (`id`);
