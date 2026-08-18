#!/usr/bin/env bash
# [모듈] api/deploy/deploy.sh
# [담당] 공통
# [역할] 코드 배포 + systemd 서비스 재시작 스크립트 (VM 대상, Docker 없음).
# [구현할 것]
#   - git pull 또는 아티팩트 배치
#   - pip install (pyproject.toml 기반)
#   - alembic upgrade head (scripts/migrate.sh 호출)
#   - systemctl restart sesac-api sesac-sweeper sesac-dispatcher
# [의존] api/scripts/migrate.sh, systemd 유닛 3종
# [호출자] 수동 실행 또는 CI
# [주의] bastion/배포 대상 VM에서만 실행. 마이그레이션은 반드시 writer 접속.
# [TODO] 구현 필요
