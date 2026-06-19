import app.services.geo.nominatim as nom


class FakeResp:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise nom.httpx.HTTPStatusError("error", request=None, response=None)


def test_geocode_parses_boundingbox(monkeypatch):
    payload = [{"boundingbox": ["-34.60", "-34.50", "-58.50", "-58.40"]}]
    monkeypatch.setattr(nom.httpx, "get", lambda url, **kw: FakeResp(payload))
    bbox = nom.geocode("Palermo, Buenos Aires")
    assert bbox == [-34.60, -34.50, -58.50, -58.40]


def test_geocode_returns_none_when_empty(monkeypatch):
    monkeypatch.setattr(nom.httpx, "get", lambda url, **kw: FakeResp([]))
    assert nom.geocode("Lugar inexistente") is None
