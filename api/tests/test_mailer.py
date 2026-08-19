"""
[모듈] api/tests/test_mailer.py
[담당] A
[역할] core/mailer.send_mail 테스트 — SMTP_HOST 미설정 시 로그 스텁 폴백,
       설정 시 실제 smtplib 경로(TLS/로그인/발송 호출) 검증.

[구현할 것]
- test_send_mail_without_smtp_host_does_not_raise
- test_send_mail_with_smtp_host_calls_smtplib
- test_send_mail_without_tls_skips_starttls
- test_send_mail_without_username_skips_login

[의존]
- tests.conftest (환경변수 설정 시점 보장)
- unittest.mock (smtplib.SMTP 목킹)

[호출자]
- pytest

[주의]
- app.core.config.get_settings()는 lru_cache라 conftest.py에서 이미 로드된
  Settings 싱글턴을 그대로 재사용한다. SMTP_HOST가 기본값(빈 문자열)이므로
  대부분의 테스트는 스텁 경로를 탄다. 실제 SMTP 경로를 테스트하려면
  get_settings()가 반환하는 Settings 객체의 필드를 monkeypatch로 직접 덮어쓴다.
"""

from unittest.mock import MagicMock, patch

from app.core.config import get_settings
from app.core.mailer import send_mail


def test_send_mail_without_smtp_host_does_not_raise():
    # conftest.py가 SMTP_HOST를 설정하지 않으므로 기본값(빈 문자열) 그대로다.
    send_mail("someone@test.com", "제목", "본문")  # 예외 없이 로그만 남기고 끝나야 함


def test_send_mail_with_smtp_host_calls_smtplib(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_port", 587)
    monkeypatch.setattr(settings, "smtp_use_tls", True)
    monkeypatch.setattr(settings, "smtp_username", "user@example.com")
    monkeypatch.setattr(settings, "smtp_password", "secret")

    mock_server = MagicMock()
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__.return_value = mock_server

    with patch("app.core.mailer.smtplib.SMTP", mock_smtp_cls):
        send_mail("someone@test.com", "subject-line", "body-text")

    mock_smtp_cls.assert_called_once_with("smtp.example.com", 587, timeout=10)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@example.com", "secret")
    mock_server.sendmail.assert_called_once()
    args = mock_server.sendmail.call_args.args
    assert args[0] == settings.smtp_from_email
    assert args[1] == ["someone@test.com"]
    # 한글은 MIME에서 base64로 인코딩되므로, ASCII 제목으로 평문 포함 여부를 확인한다.
    assert "subject-line" in args[2]


def test_send_mail_without_tls_skips_starttls(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_use_tls", False)
    monkeypatch.setattr(settings, "smtp_username", "")

    mock_server = MagicMock()
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__.return_value = mock_server

    with patch("app.core.mailer.smtplib.SMTP", mock_smtp_cls):
        send_mail("someone@test.com", "제목", "본문")

    mock_server.starttls.assert_not_called()
    mock_server.login.assert_not_called()
    mock_server.sendmail.assert_called_once()
