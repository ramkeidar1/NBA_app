from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from jose import jwt

import app.config as cfg
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def make_token():
    def _factory(expired: bool = False) -> str:
        delta = timedelta(minutes=-1) if expired else timedelta(minutes=15)
        exp = datetime.now(timezone.utc) + delta
        return jwt.encode(
            {"sub": "test-user-id", "exp": exp},
            cfg.JWT_SECRET,
            algorithm=cfg.JWT_ALGORITHM,
        )
    return _factory
