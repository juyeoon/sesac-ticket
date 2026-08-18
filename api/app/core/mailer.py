"""
[모듈] api/app/core/mailer.py
[담당] 공통
[역할] 이메일 발송 스텁. 실제 SMTP/이메일 서비스 연동 전까지 로그로만 기록한다.

[구현할 것]
- send_mail(to, subject, body) -> None

[의존]
- 없음 (실제 SMTP 미연동 — 로그 출력만)

[호출자]
- app.domains.auth.service (비밀번호 재설정 링크, 이메일 인증 코드 발송)

[주의]
- 실제 메일 발송 인프라(SMTP/SES 등)가 준비되면 이 함수 내부만 교체하면 된다.
  호출부는 이 함수의 시그니처에만 의존하도록 유지할 것.
- 스텁이므로 실패가 없다(항상 성공). 실제 연동 시 예외 처리를 추가해야 한다.
"""

import logging

logger = logging.getLogger(__name__)


def send_mail(to: str, subject: str, body: str) -> None:
    logger.info("mail (stub, not actually sent): to=%s subject=%s body=%s", to, subject, body)
