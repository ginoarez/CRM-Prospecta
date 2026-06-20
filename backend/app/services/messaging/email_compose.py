from app.services.messaging.wa_link import render_template


def render_email(template, lead) -> tuple[str, str]:
    subject = render_template(template.subject or "", lead)
    body = render_template(template.body, lead)
    return subject, body
