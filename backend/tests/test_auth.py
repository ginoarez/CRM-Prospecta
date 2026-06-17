def test_register_and_login(client):
    r = client.post("/auth/register", json={"email": "u@u.com", "password": "secret123", "full_name": "U"})
    assert r.status_code == 201
    assert r.json()["email"] == "u@u.com"

    r = client.post("/auth/login", json={"email": "u@u.com", "password": "secret123"})
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"] and body["refresh_token"]


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "u@u.com", "password": "secret123"})
    r = client.post("/auth/login", json={"email": "u@u.com", "password": "nope"})
    assert r.status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401


def test_me_returns_current_user(client, auth_headers):
    r = client.get("/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "a@a.com"


def test_refresh(client):
    client.post("/auth/register", json={"email": "u@u.com", "password": "secret123"})
    tokens = client.post("/auth/login", json={"email": "u@u.com", "password": "secret123"}).json()
    r = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    assert r.json()["access_token"]
