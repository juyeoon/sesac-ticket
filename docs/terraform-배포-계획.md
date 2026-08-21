# Terraform 프로덕션 배포 계획 (sesac-ticket)

> 근거 자료: `sesac ticket aws.drawio.png`, 현재 `terraform/` 구성(테스트용 1-AZ/퍼블릭 서브넷 단일 구성)
> 목표: 다이어그램에 정의된 멀티 AZ / public-private 분리 아키텍처를 Terraform으로 재구축

## 0. 현재 상태 vs 목표 아키텍처

| 항목 | 현재 (`terraform/`) | 목표 (다이어그램) |
|---|---|---|
| 서브넷 | 퍼블릭 1개 (10.0.1.0/24), AZ 1개 | Public 2개 + Private(web/api/cache/db) 각 2개, AZ 2개(2a/2c) |
| DB/Cache 위치 | 퍼블릭 서브넷 (SG로만 차단) | Private 서브넷 (`sstk-priv-cache-a`, `sstk-priv-db-a`) |
| 진입점 | work 인스턴스에 퍼블릭 IP 직결 | Route53 → ACM(HTTPS) → `alb-pub` → ASG(web) → `alb-int` → ASG(api) |
| 관리 접근 | work SG에 SSH 직접 허용 | `bastion` 경유 (퍼블릭 서브넷, `sstk-bastion-sg`) |
| 이중화 | 없음 (인스턴스 1대씩 고정) | web/api는 ASG로 2a/2c 양쪽 배치, DB/Cache/NAT/bastion은 2a 단일(비용 절감) |
| 아웃바운드 | 인스턴스에 EIP 직결 | Private 서브넷은 NAT Gateway 경유 |

현재 `terraform/`은 `.gitignore`에 등록된 개인 테스트용이므로 그대로 확장하지 않고, **신규 모듈 구조로 처음부터 다시 짠다.**

## 1단계 — Terraform 프로젝트 구조 설계

- 원격 backend 구성: S3(state) + DynamoDB(lock) 신규 생성 (현재는 local state라 팀 공유 불가)
- 디렉터리를 기능별 모듈로 분리:
  ```
  terraform/
    envs/prod/            # root module (backend, provider, variable 값)
    modules/
      network/            # VPC, subnet x8, IGW, NAT, route table
      security-groups/     # bastion/alb-pub/alb-int/web/api/valkey/mysql SG
      acm-dns/             # ACM 인증서 + Route53 레코드
      alb/                 # public/internal ALB + target group + listener (재사용 모듈)
      compute-web/         # launch template + ASG (web)
      compute-api/         # launch template + ASG (api)
      compute-data/        # bastion, valkey, mysql EC2
  ```
- `terraform.tfvars`에 민감정보(db 비밀번호, jwt_secret 등) 분리, `.gitignore` 유지
- 상태 격리: 이후 스테이징 환경이 필요해지면 `envs/staging` 추가할 수 있게 변수화

## 2단계 — 네트워킹 (network 모듈)

1. `aws_vpc` `sstk-vpc` (10.0.0.0/16) 생성, DNS 옵션 활성화
2. 서브넷 8개 생성 (CIDR은 다이어그램 값 그대로 사용)
   - Public: `sstk-pub-a`(10.0.0.0/24, 2a), `sstk-pub-c`(10.0.1.0/24, 2c)
   - Private-web: `sstk-priv-web-a`(10.0.10.0/24), `sstk-priv-web-c`(10.0.11.0/24)
   - Private-api: `sstk-priv-api-a`(10.0.20.0/24), `sstk-priv-api-c`(10.0.21.0/24)
   - Private-cache: `sstk-priv-cache-a`(10.0.30.0/24), `sstk-priv-cache-c`(10.0.31.0/24)
   - Private-db: `sstk-priv-db-a`(10.0.40.0/24), `sstk-priv-db-c`(10.0.41.0/24)
3. `aws_internet_gateway` 생성 후 VPC에 attach
4. `aws_nat_gateway` + EIP를 `sstk-pub-a`에 1개만 생성 (다이어그램상 2c에는 NAT 없음 → private 서브넷들은 모두 이 NAT 하나를 공유)
5. 라우트 테이블
   - Public RT: `0.0.0.0/0 → IGW`, public 서브넷 2개 연결
   - Private RT: `0.0.0.0/0 → NAT Gateway`, private 서브넷 8개(web/api/cache/db × 2AZ) 전부 연결
6. `terraform plan`으로 CIDR 겹침/개수 검증 후 apply

## 3단계 — 보안 그룹 (security-groups 모듈)

다이어그램의 SG 6종을 각각 최소 권한으로 정의:

| SG | Ingress 허용 | 비고 |
|---|---|---|
| `sstk-bastion-sg` | 관리자 IP에서 22 | 퍼블릭 서브넷 배치 |
| `alb-pub-sg` | 인터넷에서 443(+80→443 리다이렉트용 80) | ACM 인증서 붙는 ALB |
| `sstk-web-sg` | `alb-pub-sg`에서 앱 포트만 | web ASG 인스턴스 |
| `alb-int-sg` | `sstk-web-sg`에서 앱 포트 | 내부 ALB, 인터넷 노출 없음 |
| `sstk-api-sg` | `alb-int-sg`에서 API 포트, `sstk-bastion-sg`에서 22 | api ASG 인스턴스 |
| `sstk-valkey-sg` | `sstk-api-sg`에서 6379, `sstk-bastion-sg`에서 22 | private-cache |
| `sstk-mysql-sg` | `sstk-api-sg`에서 3306, `sstk-bastion-sg`에서 22 | private-db |

- 기존 테스트 구성처럼 "SG 체이닝"(`security_groups = [다른 SG.id]`)만 쓰고 CIDR 기반 내부 허용은 지양 → 그대로 재사용 가능한 패턴

## 4단계 — ACM / Route53

1. Route53에 도메인 호스팅 영역이 있는지 확인 (없으면 등록 필요 — 수동/별도 승인 필요 항목)
2. `aws_acm_certificate` (DNS 검증) 발급, `aws_route53_record`로 검증 레코드 자동 생성
3. `aws_acm_certificate_validation`으로 발급 완료까지 대기
4. 발급된 인증서 ARN을 `alb-pub` HTTPS 리스너(443)에 연결
5. `aws_route53_record` (A/Alias)로 도메인 → `alb-pub` 연결

> ⚠️ 도메인 소유/Route53 위임 여부는 사용자 확인 필요 — 진행 전에 도메인명을 확정해야 함

## 5단계 — 데이터 계층 (compute-data 모듈): mysql, valkey, bastion

- 기존 `instances.tf`의 `db_user_data.sh.tpl`/`redis_user_data.sh.tpl` 로직(Docker로 mysql:8.0 / valkey 컨테이너 기동)은 그대로 재사용
- 배치만 변경: `sstk-priv-db-a`(mysql), `sstk-priv-cache-a`(valkey) — **퍼블릭 IP 미할당**
- `bastion` EC2를 `sstk-pub-a`에 신규 생성 (SSM Session Manager 사용 권장 — 키페어/22 노출 최소화 대안으로 검토)
- DB 초기화 SQL(`sesac_ticket_init.sql`) 적용 방식 동일하게 유지
- 이 단계 완료 후 bastion을 통해 mysql/valkey 컨테이너 정상 기동 확인

## 6단계 — API 계층: alb-int + ASG(api)

1. `aws_lb` internal (`internal = true`), `sstk-priv-api-a/c` 서브넷에 배치, `alb-int-sg` 적용
2. Target Group(HTTP, health check `/health` 등 api 헬스체크 경로 확인 필요) 생성
3. `aws_launch_template` 작성: 기존 `work_user_data.sh.tpl`(git clone → venv → systemd로 uvicorn/queue_dispatcher 구동) 로직을 api 전용으로 재정리
   - user_data에서 db/redis 접속 정보는 5단계에서 만든 private IP(또는 내부 DNS)로 주입
4. `aws_autoscaling_group`: `sstk-priv-api-a`, `sstk-priv-api-c`에 걸쳐 최소 2대(AZ당 1대 이상), target group 연결
5. Scaling policy는 우선 고정 용량(min=desired=max=2)으로 시작 → 이후 CPU/요청수 기반 정책 추가 검토

## 7단계 — 웹 계층: alb-pub + ASG(web)

1. `aws_lb` internet-facing, `sstk-pub-a/c`에 배치, `alb-pub-sg` 적용, 443 리스너에 4단계 ACM 인증서 연결
2. Target Group → `sstk-web-sg` 인스턴스
3. `aws_launch_template`(web): 정적 자산/프론트엔드 서빙 or 리버스 프록시 설정 — 현재 리포에 web 전용 배포 스크립트가 있는지 `api/`, 프론트 코드 위치 확인 필요 (없다면 이 단계 전에 web 서버 구성 방식부터 확정)
4. `aws_autoscaling_group`: `sstk-priv-web-a`, `sstk-priv-web-c`에 배치 (인스턴스 자체는 private subnet, 트래픽은 `alb-pub`을 통해서만 유입)
5. web → api 통신은 `alb-int`의 내부 DNS로 연결되도록 web 인스턴스 설정

## 8단계 — 통합 검증

- bastion → api 인스턴스 SSH 접속 확인
- Route53 도메인 → alb-pub(443) → web ASG → alb-int → api ASG → mysql/valkey 전 구간 트래픽 흐름 실제 요청으로 검증
- ASG 인스턴스 강제 종료 후 자동 복구(재기동) 확인 (최소 1회 장애 시뮬레이션)
- CloudWatch 알람(ASG 헬스체크 실패, ALB 5xx 등) 기본 셋 추가 검토

## 9단계 — 컷오버 & 정리

1. 기존 테스트용 `terraform/`(퍼블릭 EC2 3대) 트래픽을 신규 아키텍처로 전환 후 `terraform destroy`로 정리 (과금 방지)
2. 신규 `envs/prod` state를 S3 backend로 최종 이관 확인
3. `docs/`에 운영 런북(재해복구, 스케일 조정, 인증서 갱신 주기 등) 문서화

## 확인이 필요한 미결정 사항

- [ ] 사용할 도메인명 및 Route53 호스팅 영역 존재 여부
- [ ] web 계층에서 서빙할 실제 프론트엔드 산출물/빌드 방식 (현재 리포 구조상 web 전용 코드 위치 미확인)
- [ ] bastion 접근 방식: 키페어 SSH vs SSM Session Manager
- [ ] api/health 체크 엔드포인트 경로
- [ ] mysql/valkey 백업 정책 (다이어그램에는 단일 AZ로만 표시되어 있어 DR 정책 별도 필요)
