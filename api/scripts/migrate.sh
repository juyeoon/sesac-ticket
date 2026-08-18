#!/usr/bin/env bash
# [모듈] api/scripts/migrate.sh
# [담당] 공통
# [역할] alembic upgrade head 실행 래퍼.
# [구현할 것]
#   - cd api && alembic upgrade head
#   - 실패 시 비영(non-zero) 종료 코드 반환
# [의존] api/alembic/env.py
# [호출자] api/deploy/deploy.sh, 수동 실행(bastion)
# [주의] bastion(또는 writer DB에 접근 가능한 호스트)에서만 실행할 것.
# [TODO] 구현 필요
