import sys
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import OperationalError

from app import cli


def test_database_failure_does_not_expose_sql_parameters(monkeypatch):
    engine = MagicMock()
    db = MagicMock()
    db.__enter__.return_value = db
    db.execute.side_effect = OperationalError(
        "fixture SQL", {"password_hash": "redaction-test-marker"}, Exception()
    )
    monkeypatch.setattr(cli, "build_engine", lambda **kwargs: engine)
    monkeypatch.setattr(cli, "Session", lambda engine: db)
    monkeypatch.setattr(sys, "argv", ["cli", "bootstrap-admin", "test_admin"])
    with pytest.raises(SystemExit) as failure:
        cli.main()
    assert str(failure.value) == "資料庫操作失敗，請稍後重試"
    assert failure.value.__suppress_context__
    engine.dispose.assert_called_once()
