import os

os.environ.setdefault(
    "DATABASE_URL", "postgresql+psycopg://prospecta:prospecta@localhost:5432/prospecta_test"
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
import app.models  # noqa: F401

engine = create_engine(settings.DATABASE_URL)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db):
    def _get_db():
        yield db
    app.dependency_overrides[get_db] = _get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    client.post("/auth/register", json={"email": "a@a.com", "password": "secret123", "full_name": "A"})
    r = client.post("/auth/login", json={"email": "a@a.com", "password": "secret123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}
