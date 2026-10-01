"""Prove the existing outage regression catches a bypassed DB probe."""
from unittest.mock import patch

import pytest

from app import main

with patch.object(main, "check_database", lambda engine: None):
    result = pytest.main(
        ["tests/test_health.py::test_readiness_rejects_unavailable_database", "-q"]
    )
if result != pytest.ExitCode.TESTS_FAILED:
    raise SystemExit("Mutation not killed by the outage regression")
print("PASS: fixed-success mutation rejected by existing outage regression")
