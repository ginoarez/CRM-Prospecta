import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import settings


def send_email(to: str, subject: str, body: str) -> None:
    if not settings.SMTP_HOST:
        raise RuntimeError("SMTP no configurado (SMTP_HOST vacío)")

    msg = EmailMessage()
    msg["From"] = formataddr((settings.SMTP_FROM_NAME, settings.SMTP_FROM))
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        if settings.SMTP_STARTTLS:
            smtp.starttls()
        if settings.SMTP_USER:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASS)
        smtp.send_message(msg)
