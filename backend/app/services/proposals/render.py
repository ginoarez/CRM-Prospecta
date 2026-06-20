import os
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_html(proposal, lead) -> str:
    template = _env.get_template("proposal.html")
    return template.render(
        lead=lead,
        content=proposal.content or {},
        agency_name=settings.AGENCY_NAME,
        agency_tagline=settings.AGENCY_TAGLINE,
        agency_email=settings.AGENCY_EMAIL,
        agency_phone=settings.AGENCY_PHONE,
        logo_url=settings.AGENCY_LOGO_URL,
        color=settings.AGENCY_COLOR,
        date=date.today().isoformat(),
    )


def render_pdf(proposal, lead, *, storage_dir: str | None = None) -> str:
    from weasyprint import HTML  # import perezoso: evita la dependencia nativa en tests

    out_dir = storage_dir or settings.PROPOSALS_DIR
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{proposal.id}.pdf")
    HTML(string=render_html(proposal, lead)).write_pdf(path)
    return path
