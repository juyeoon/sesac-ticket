"""
[모듈] api/app/core/mailer.py
[담당] 공통
[역할] 이메일 발송. `SMTP_HOST`가 설정되어 있으면 실제 SMTP로 발송하고,
       비어있으면(로컬/테스트 기본값) 로그로만 남긴다.

[구현할 것]
- send_mail(to, subject, body) -> None

[의존]
- smtplib, email.mime.text (표준 라이브러리, 추가 패키지 의존성 없음)
- app.core.config

[호출자]
- app.domains.auth.service (비밀번호 재설정 링크, 이메일 인증 코드 발송)

[주의]
- `SMTP_HOST`가 비어있으면 실제 발송을 시도하지 않고 로그만 남긴다. 로컬 개발/테스트
  환경에서 실제 메일 서버 없이도 동작하게 하기 위한 의도적인 폴백이며,
  `tests/conftest.py`도 SMTP_HOST를 설정하지 않으므로 테스트는 항상 이 경로를 탄다.
- 발송 실패(SMTPException 등)는 그대로 올린다 — 호출부가 잡아서 처리하지 않는 한
  요청은 500으로 응답한다. 이메일 존재 여부를 숨기는 보안 요구사항과는 무관한
  인프라 실패이므로 조용히 삼키지 않는다.
"""

import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_mail(to: str, subject: str, body: str) -> None:
    settings = get_settings()

    if not settings.smtp_host:
        logger.info(
            "mail (stub, SMTP_HOST 미설정): to=%s subject=%s body=%s", to, subject, body
        )
        return

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = to

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.smtp_from_email, [to], message.as_string())

    logger.info("mail sent via SMTP: to=%s subject=%s", to, subject)
