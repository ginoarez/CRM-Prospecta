from app.services.geo import categories


def test_every_category_has_label_and_tags():
    assert len(categories.CATEGORIES) >= 11
    for key, cat in categories.CATEGORIES.items():
        assert cat["label"], f"{key} sin label"
        assert cat["tags"], f"{key} sin tags"


def test_get_tags_known_and_unknown():
    assert categories.get_tags("gym")
    assert categories.get_tags("no-existe") is None


def test_categories_endpoint(client, auth_headers):
    r = client.get("/geo/categories", headers=auth_headers)
    assert r.status_code == 200
    keys = {c["key"] for c in r.json()}
    assert "gym" in keys and "restaurant" in keys


def test_categories_requires_auth(client):
    assert client.get("/geo/categories").status_code == 401
