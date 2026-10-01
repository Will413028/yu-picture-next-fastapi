from unittest.mock import sentinel

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import security

ORIGIN = "http://127.0.0.1:3309"


def test_non_ascii_csrf_is_rejected_without_server_error(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", ORIGIN)
    monkeypatch.setattr(
        security, "session_for_request", lambda request, db: sentinel.row
    )
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/",
            "headers": [
                (b"origin", ORIGIN.encode()),
                (b"cookie", f"{security.COOKIE_NAME}={'x' * 43}".encode()),
                (b"x-csrf-token", b"\xff"),
            ],
        }
    )
    with pytest.raises(HTTPException) as failure:
        security.require_csrf(request, sentinel.db)
    assert failure.value.status_code == 403
    valid = Request(
        {
            **request.scope,
            "headers": [
                *request.scope["headers"][:-1],
                (b"x-csrf-token", security.csrf_for_token("x" * 43).encode()),
            ],
        }
    )
    assert security.require_csrf(valid, sentinel.db) is sentinel.row
