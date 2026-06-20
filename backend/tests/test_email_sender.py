import smtplib

import pytest

from app.core.config import settings
from app.services.email import sender


class FakeSMTP:
    instances = []

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tls = False
        self.logged_in = None
        self.sent = []
        FakeSMTP.instances.append(self)

    def starttls(self):
        self.tls = True

    def login(self, user, password):
        self.logged_in = (user, password)

    def send_message(self, msg):
        self.sent.append(msg)

    def quit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture(autouse=True)
def _smtp(monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)


def test_send_email_raises_when_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "SMTP_HOST", "")
    with pytest.raises(RuntimeError):
        sender.send_email("to@x.com", "s", "b")


def test_send_email_builds_and_sends(monkeypatch):
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test")
    monkeypatch.setattr(settings, "SMTP_USER", "u")
    monkeypatch.setattr(settings, "SMTP_PASS", "p")
    monkeypatch.setattr(settings, "SMTP_STARTTLS", True)
    sender.send_email("to@x.com", "Asunto", "Cuerpo")
    smtp = FakeSMTP.instances[-1]
    assert smtp.tls is True
    assert smtp.logged_in == ("u", "p")
    assert len(smtp.sent) == 1
    msg = smtp.sent[0]
    assert msg["To"] == "to@x.com"
    assert msg["Subject"] == "Asunto"
    assert msg.get_content().strip() == "Cuerpo"


def test_send_email_no_login_when_no_user(monkeypatch):
    monkeypatch.setattr(settings, "SMTP_HOST", "smtp.test")
    monkeypatch.setattr(settings, "SMTP_USER", "")
    monkeypatch.setattr(settings, "SMTP_STARTTLS", False)
    sender.send_email("to@x.com", "s", "b")
    smtp = FakeSMTP.instances[-1]
    assert smtp.logged_in is None
    assert smtp.tls is False
