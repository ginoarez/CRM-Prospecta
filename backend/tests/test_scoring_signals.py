import app.services.scoring.signals as sig

HTML = """
<html><head>
<meta name="viewport" content="width=device-width">
</head><body>
<script src="https://widget.intercom.io/widget/abc"></script>
<a href="https://instagram.com/foo">ig</a>
<a href="https://calendly.com/foo">book</a>
</body></html>
"""


def test_parse_signals_detects_flags():
    s = sig.parse_signals(HTML, "https://foo.com")
    assert s["website_reachable"] is True
    assert s["https"] is True
    assert s["has_viewport_meta"] is True
    assert s["has_chat_widget"] is True
    assert s["has_booking"] is True
    assert "instagram" in s["social_links"]


def test_parse_signals_minimal_html():
    s = sig.parse_signals("<html><body>hola</body></html>", "http://foo.com")
    assert s["https"] is False
    assert s["has_viewport_meta"] is False
    assert s["has_chat_widget"] is False
    assert s["social_links"] == []


def test_collect_signals_no_website():
    assert sig.collect_signals(None) == {"website_reachable": False}


def test_collect_signals_fetch_fails(monkeypatch):
    monkeypatch.setattr(sig, "fetch_html", lambda w: None)
    assert sig.collect_signals("http://foo.com") == {"website_reachable": False}


def test_collect_signals_parses(monkeypatch):
    monkeypatch.setattr(sig, "fetch_html", lambda w: HTML)
    s = sig.collect_signals("https://foo.com")
    assert s["website_reachable"] is True
    assert s["has_chat_widget"] is True
