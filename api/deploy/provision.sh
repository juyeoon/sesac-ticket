#!/usr/bin/env bash
# [모듈] api/deploy/provision.sh
# [담당] 공통
# [역할] 신규 VM 최초 프로비저닝 스크립트 (런타임/의존성 설치, systemd 유닛 등록).
# [구현할 것]
#   - Python 런타임 설치
#   - pyproject.toml 기반 의존성 설치
#   - systemd 유닛 파일 복사 및 systemctl enable
#   - .env 파일 배치 안내(비밀값은 별도 채널로 전달)
# [의존] api/deploy/systemd/*.service, api/pyproject.toml
# [호출자] 최초 VM 세팅 시 1회 실행
# [주의] Docker를 쓰지 않는 구성이므로 VM 로컬 Python 버전과 의존성 충돌에 유의.
# [TODO] 구현 필요
