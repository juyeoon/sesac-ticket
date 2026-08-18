#!/usr/bin/env bash
# [모듈] api/scripts/migrate.sh
# [담당] 공통
# [역할] DB 스키마 셋업/갱신 래퍼.
#
# 방식: raw SQL 우선 (2026-08-18 결정)
#   - 최초 스키마는 Alembic이 아니라 api/scripts/sql/sesac_ticket_init.sql로 만든다.
#   - Alembic은 그 이후 `stamp`로 현재 상태를 등록하고, 다음 스키마 변경부터
#     `alembic revision --autogenerate`로 diff를 쌓는 용도로 쓴다.
#
# 사용법:
#   ./migrate.sh init      # 최초 1회: init.sql 실행 + alembic stamp
#   ./migrate.sh seed      # (선택) 더미 데이터 주입
#   ./migrate.sh upgrade   # 이후 알렘빅 리비전 반영 (alembic upgrade head)
#
# [의존] api/alembic/env.py, api/scripts/sql/sesac_ticket_init.sql
# [호출자] api/deploy/deploy.sh, 수동 실행(bastion)
# [주의] bastion(또는 writer DB에 접근 가능한 호스트)에서만 실행할 것.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SQL_DIR="$SCRIPT_DIR/sql"

: "${MYSQL_HOST:=127.0.0.1}"
: "${MYSQL_PORT:=3306}"
: "${MYSQL_USER:=root}"

case "${1:-}" in
  init)
    mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p < "$SQL_DIR/sesac_ticket_init.sql"
    (cd "$API_DIR" && alembic stamp 0001_baseline)
    ;;
  seed)
    mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p sesac_ticket < "$SQL_DIR/sesac_ticket_dummy_data_1.sql"
    ;;
  upgrade)
    (cd "$API_DIR" && alembic upgrade head)
    ;;
  *)
    echo "usage: $0 {init|seed|upgrade}" >&2
    exit 1
    ;;
esac
