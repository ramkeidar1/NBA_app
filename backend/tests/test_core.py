from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from jose import jwt

import app.config as cfg
from app.auth.utils import decode_access_token
from app.orchestrator import run_pipeline


# ── 1. Unit: expired token raises ValueError ──────────────────────────────────

def test_decode_expired_token_raises():
    expired_token = jwt.encode(
        {"sub": "user-1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        cfg.JWT_SECRET,
        algorithm=cfg.JWT_ALGORITHM,
    )
    with pytest.raises(ValueError, match="Invalid access token"):
        decode_access_token(expired_token)


# ── 2. Integration: login with bad credentials returns 401 ────────────────────

def test_login_bad_credentials_returns_401(client):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    with patch("app.api.auth.get_supabase", return_value=mock_client):
        res = client.post("/auth/login", json={"email": "nobody@example.com", "password": "wrong"})

    assert res.status_code == 401


# ── 3. Integration: stream with no token returns 422 ─────────────────────────

def test_stream_missing_token_returns_422(client):
    res = client.get("/api/analysis/stream/LAL_GSW")
    assert res.status_code == 422


# ── 4. Integration: stream with invalid token returns 401 ────────────────────

def test_stream_invalid_token_returns_401(client):
    res = client.get("/api/analysis/stream/LAL_GSW?token=not.a.valid.token")
    assert res.status_code == 401


# ── 5. Pipeline: DUMMY_MODE completes and emits a done event ─────────────────

async def test_run_pipeline_dummy_completes():
    events = []
    async for event in run_pipeline("LAL_GSW", mode="hard", dummy=True):
        events.append(event)

    event_names = [e.event_name for e in events]
    assert "done" in event_names
