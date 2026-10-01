"""Mutation checks run only against randomly named test-owned schemas."""

from unittest.mock import patch

import pytest
from sqlalchemy.orm import object_session

from app import main, security, users

original_factory = main.create_app

baseline = pytest.main(
    [
        "tests/test_users.py::test_csrf_and_admin_boundary",
        "tests/test_users.py::test_redemption_rollback_and_rotation",
        "-q",
    ]
)
if baseline != pytest.ExitCode.OK:
    raise SystemExit("Mutation baseline failed; no mutation result is valid")


def bypass_admin():
    app = original_factory()
    app.dependency_overrides[security.require_admin] = security.require_user
    return app


with patch.object(main, "create_app", bypass_admin):
    result = pytest.main(["tests/test_users.py::test_csrf_and_admin_boundary", "-q"])
if result != pytest.ExitCode.TESTS_FAILED:
    raise SystemExit("Admin permission mutation survived")


def premature_commit(user, code, timestamp):
    object_session(user).commit()
    raise RuntimeError("Injected non-atomic redemption")


with patch.object(users, "apply_membership", premature_commit):
    # This test replaces apply_membership to inject failure itself, so target its
    # failure hook through a wrapper test plugin instead.
    class ReplaceFailure:
        @pytest.hookimpl(tryfirst=True)
        def pytest_runtest_call(self, item):
            if item.name == "test_redemption_rollback_and_rotation":
                monkeypatch = item.funcargs["monkeypatch"]
                original_setattr = monkeypatch.setattr

                def replace(target, name, value):
                    if target is users and name == "apply_membership":
                        value = premature_commit
                    original_setattr(target, name, value)

                monkeypatch.setattr = replace

    result = pytest.main(
        ["tests/test_users.py::test_redemption_rollback_and_rotation", "-q"],
        plugins=[ReplaceFailure()],
    )
if result != pytest.ExitCode.TESTS_FAILED:
    raise SystemExit("Atomic redemption mutation survived")
print("PASS: admin bypass and premature commit mutations rejected")
