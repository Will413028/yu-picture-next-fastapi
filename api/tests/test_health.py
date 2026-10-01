from time import monotonic, sleep
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app import main


@pytest.fixture
def disconnected_client(monkeypatch):
    engine = MagicMock()
    engine.connect.side_effect = OperationalError("unavailable", {}, Exception())
    monkeypatch.setattr(main, "build_engine", lambda: engine)
    with TestClient(main.create_app()) as client:
        yield client
    engine.dispose.assert_called_once()


def test_liveness_does_not_depend_on_database(disconnected_client):
    response = disconnected_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    disconnected_client.app.state.engine.connect.assert_not_called()


def test_readiness_rejects_unavailable_database(disconnected_client):
    response = disconnected_client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "disconnected"}
    assert response.headers["cache-control"] == "no-store"


def test_readiness_contract_with_real_postgres():
    with TestClient(main.create_app()) as client:
        deadline = monotonic() + 20
        while True:
            response = client.get("/api/v1/ready")
            if response.status_code == 200 or monotonic() >= deadline:
                break
            assert response.status_code == 503
            sleep(0.25)
        assert response.status_code == 200
        assert response.json() == {"status": "ready", "database": "connected"}


def test_schema_declares_unavailable_response(disconnected_client):
    schema = disconnected_client.get("/openapi.json").json()
    assert "503" in schema["paths"]["/api/v1/ready"]["get"]["responses"]
