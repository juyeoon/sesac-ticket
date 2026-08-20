sesac-ticket/
├── web/ # ─── web-a / web-c 배포 단위
│ ├── frontend/ # Vite + React 소스
│ │ ├── src/
│ │ ├── .env.production # VITE_API_BASE=/api (동일 오리진)
│ │ └── package.json
│ └── deploy/
│ ├── nginx/sesac-web.conf # 정적 서빙 + /api → alb-int proxy_pass
│ ├── systemd/ # (nginx는 패키지 유닛 사용, 여긴 오버라이드만)
│ ├── provision.sh # nginx, node 설치
│ └── deploy.sh # build → /var/www/sesac → nginx reload
│
├── api/ # ─── api-a / api-c 배포 단위
│ ├── app/ # (3장에서 상술)
│ ├── alembic/
│ ├── scripts/
│ │ ├── seed.py
│ │ └── migrate.sh # ★ ASG 인스턴스가 아닌 bastion에서만 실행
│ ├── tests/
│ ├── gunicorn.conf.py
│ ├── pyproject.toml
│ └── deploy/
│ ├── systemd/
│ │ ├── sesac-api.service
│ │ ├── sesac-sweeper.service
│ │ └── sesac-dispatcher.service
│ ├── env/api.env.example # 실물은 /etc/sesac/api.env
│ ├── provision.sh
│ └── deploy.sh
│
├── infra/ # ─── 수동 관리 인스턴스 + 네트워크
│ ├── mysql/
│ │ ├── master/my.cnf # server_id=1, binlog, GTID
│ │ ├── replica/my.cnf # server_id=2, read_only=ON
│ │ ├── setup-replication.md
│ │ └── init/schema.sql # (Alembic이 주도, 여긴 계정/권한만)
│ ├── valkey/
│ │ ├── master/valkey.conf
│ │ ├── replica/valkey.conf # replicaof <master-ip> 6379
│ │ └── setup-replication.md
│ ├── bastion/
│ │ └── provision.sh
│ ├── network/
│ │ ├── sg-matrix.md # ★ SG 간 참조 규칙 표 (아래 4장)
│ │ └── subnet-plan.md
│ └── diagrams/
│ └── sesac-aws-architecture.png
│
└── docs/
├── api-contract.md
├── seat-state-machine.md
└── runbook.md # 배포/롤백/장애 대응
