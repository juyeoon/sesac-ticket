"""
[모듈] api/gunicorn.conf.py
[담당] 공통
[역할] gunicorn 실행 설정(worker 클래스/개수, bind, timeout 등).

[구현할 것]
- bind = "0.0.0.0:8000"
- workers = <CPU 코어 수 기반 계산 함수 또는 고정값>
- worker_class = "uvicorn.workers.UvicornWorker"
- timeout, graceful_timeout
- loglevel, accesslog, errorlog

[의존]
- app.core.config (INSTANCE_ID 등 환경별 값 참조 시)

[호출자]
- systemd 서비스 (api/deploy/systemd/sesac-api.service)

[주의]
- ALB idle timeout(기본 60초)보다 gunicorn timeout을 짧게 잡으면 정상 처리 중인
  요청도 워커가 강제 종료될 수 있으니, ALB 쪽 idle timeout과 정합성을 맞출 것.

[TODO] 구현 필요
"""
