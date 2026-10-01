import secrets
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session, object_session

from app import main, users
from app.database import build_engine
from app.models import AuthSession, Base, User, VipCode
from app.security import HASHER, digest

ORIGIN = "http://127.0.0.1:3309"


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    application_engine = build_engine()
    root = build_engine(connect_timeout=30, statement_timeout_ms=30000)
    schema = "test_users_" + secrets.token_hex(8)
    with root.begin() as connection:
        connection.execute(text("SET LOCAL statement_timeout = '30s'"))
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = application_engine.execution_options(schema_translate_map={None: schema})
    setup_engine = root.execution_options(schema_translate_map={None: schema})
    try:
        with setup_engine.begin() as connection:
            connection.execute(text("SET LOCAL statement_timeout = '30s'"))
            Base.metadata.create_all(connection)
        monkeypatch.setattr(main, "build_engine", lambda: engine)
        app = main.create_app()
        with TestClient(app, base_url=ORIGIN, raise_server_exceptions=False) as client:
            yield client, engine, app
    finally:
        with root.begin() as connection:
            connection.execute(text("SET LOCAL statement_timeout = '30s'"))
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        root.dispose()
        application_engine.dispose()


def unsafe(client, method, path, payload=None):
    csrf_response = client.get("/api/v1/auth/csrf")
    assert csrf_response.status_code == 200, "CSRF service unavailable"
    csrf = csrf_response.json()["csrf_token"]
    return client.request(
        method,
        "/api/v1" + path,
        json=payload,
        headers={"Origin": ORIGIN, "X-CSRF-Token": csrf},
    )


def register_login(client, account="test_user"):
    password = secrets.token_urlsafe(20)
    payload = {"account": account, "password": password}
    response = unsafe(
        client,
        "POST",
        "/auth/register",
        {
            **payload,
            "confirm_password": password,
        },
    )
    assert response.status_code == 201
    assert client.get("/api/v1/auth/me").status_code == 401
    assert unsafe(client, "POST", "/auth/login", payload).status_code == 200
    return int(response.json()["id"]), password


def test_registration_session_and_private_fields(environment):
    client, engine, _ = environment
    user_id, password = register_login(client, "Tést_User")
    view = client.get("/api/v1/auth/me").json()
    assert view["role"] == "user"
    assert not {"password_hash", "vip_code_id", "vip_code"} & view.keys()
    public = client.get(f"/api/v1/users/{user_id}").json()
    assert set(public) == {"id", "name", "avatar", "profile", "created_at"}
    with Session(engine) as db:
        user = db.get(User, user_id)
        password_is_argon2 = user.password_hash.startswith("$argon2id$")
        password_verifies = HASHER.verify(user.password_hash, password)
        assert password_is_argon2
        assert password_verifies
    assert (
        unsafe(
            client,
            "POST",
            "/auth/register",
            {
                "account": "test_user",
                "password": password,
                "confirm_password": password,
            },
        ).status_code
        == 409
    )
    assert unsafe(client, "POST", "/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401


def test_csrf_and_admin_boundary(environment):
    client, engine, _ = environment
    user_id, _ = register_login(client)
    assert client.post("/api/v1/auth/logout").status_code == 403
    assert client.get("/api/v1/admin/users").status_code == 403
    with Session(engine) as db, db.begin():
        db.get(User, user_id).role = "admin"
    assert client.get("/api/v1/admin/users?sort=password_hash").status_code == 422
    created = unsafe(
        client,
        "POST",
        "/admin/users",
        {
            "account": "other_user",
            "password": secrets.token_urlsafe(20),
        },
    )
    assert created.status_code == 201
    other = created.json()["id"]
    assert (
        unsafe(
            client,
            "PATCH",
            f"/admin/users/{other}",
            {
                "account": "changed",
            },
        ).status_code
        == 422
    )
    assert (
        unsafe(
            client,
            "PATCH",
            f"/admin/users/{other}",
            {
                "name": "新名字",
                "profile": None,
            },
        ).json()["name"]
        == "新名字"
    )
    assert unsafe(client, "DELETE", f"/admin/users/{other}").status_code == 204
    assert client.get(f"/api/v1/users/{other}").status_code == 404


def test_redemption_rollback_and_rotation(environment, monkeypatch):
    client, engine, _ = environment
    user_id, _ = register_login(client)
    code = secrets.token_urlsafe(24)
    with Session(engine) as db, db.begin():
        db.add(VipCode(digest=digest(code)))
    original = users.apply_membership

    def fail(user, *args):
        object_session(user).flush()
        raise RuntimeError("injected transaction failure")

    monkeypatch.setattr(users, "apply_membership", fail)
    assert (
        unsafe(
            client,
            "POST",
            "/membership/redemptions",
            {
                "code": code,
            },
        ).status_code
        == 500
    )
    with Session(engine) as db:
        assert db.scalar(select(VipCode)).used_by is None
        assert db.get(User, user_id).role == "user"
    monkeypatch.setattr(users, "apply_membership", original)
    with Session(engine) as db, db.begin():
        subject = db.get(User, user_id)
        subject.role = "admin"
        subject.vip_expires_at = datetime(2030, 1, 1, tzinfo=UTC)
    monkeypatch.setattr(users, "now", lambda: datetime(2024, 2, 29, tzinfo=UTC))
    stale = client.get("/api/v1/auth/csrf").json()["csrf_token"]
    result = unsafe(client, "POST", "/membership/redemptions", {"code": code})
    assert result.status_code == 200
    assert result.json()["vip_expires_at"].startswith("2025-02-28")
    assert result.json()["role"] == "vip"
    assert (
        client.post(
            "/api/v1/auth/logout",
            headers={
                "Origin": ORIGIN,
                "X-CSRF-Token": stale,
            },
        ).status_code
        == 403
    )
    assert (
        unsafe(
            client,
            "POST",
            "/membership/redemptions",
            {
                "code": code,
            },
        ).status_code
        == 409
    )


def test_code_is_consumed_once_under_concurrency(environment):
    first, engine, app = environment
    register_login(first, "first_user")
    second = TestClient(app, base_url=ORIGIN)
    register_login(second, "second_user")
    code = secrets.token_urlsafe(24)
    with Session(engine) as db, db.begin():
        db.add(VipCode(digest=digest(code)))
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(
            pool.map(
                lambda client: unsafe(
                    client,
                    "POST",
                    "/membership/redemptions",
                    {
                        "code": code,
                    },
                ),
                [first, second],
            )
        )
    assert sorted(response.status_code for response in responses) == [200, 409]
    with Session(engine) as db:
        assert len(db.scalars(select(User).where(User.role == "vip")).all()) == 1
    second.close()


@pytest.mark.parametrize("absolute", [False, True])
def test_expired_sessions_are_rejected(environment, absolute):
    client, engine, _ = environment
    user_id, _ = register_login(client)
    with Session(engine) as db, db.begin():
        row = db.scalar(select(AuthSession).where(AuthSession.user_id == user_id))
        if absolute:
            row.created_at = datetime.now(UTC) - timedelta(hours=25)
        else:
            row.last_seen_at = datetime.now(UTC) - timedelta(minutes=31)
    assert client.get("/api/v1/auth/me").status_code == 401


def test_validation_origin_cookie_and_revocation(environment):
    client, engine, _ = environment
    user_id, password = register_login(client)
    csrf = client.get("/api/v1/auth/csrf").json()["csrf_token"]
    assert (
        client.post(
            "/api/v1/auth/logout",
            headers={
                "Origin": "https://untrusted.invalid",
                "X-CSRF-Token": csrf,
            },
        ).status_code
        == 403
    )
    result = unsafe(
        client,
        "POST",
        "/auth/register",
        {
            "account": "another_user",
            "password": password,
            "confirm_password": password,
            "role": "admin",
        },
    )
    assert result.status_code == 422
    credential_was_echoed = password in result.text
    assert not credential_was_echoed
    login = unsafe(
        client,
        "POST",
        "/auth/login",
        {
            "account": "test_user",
            "password": password,
        },
    )
    assert "HttpOnly" in login.headers["set-cookie"]
    assert "SameSite=lax" in login.headers["set-cookie"]
    with Session(engine) as db, db.begin():
        db.get(User, user_id).role = "admin"
    assert (
        unsafe(
            client,
            "PATCH",
            f"/admin/users/{user_id}",
            {
                "role": "user",
            },
        ).status_code
        == 200
    )
    assert client.get("/api/v1/auth/me").status_code == 401


def test_same_user_concurrent_codes_only_one_old_session_survives(environment):
    first, engine, app = environment
    _, password = register_login(first)
    second = TestClient(app, base_url=ORIGIN)
    assert (
        unsafe(
            second,
            "POST",
            "/auth/login",
            {
                "account": "test_user",
                "password": password,
            },
        ).status_code
        == 200
    )
    codes = [secrets.token_urlsafe(24), secrets.token_urlsafe(24)]
    with Session(engine) as db, db.begin():
        db.add_all([VipCode(digest=digest(code)) for code in codes])
    tokens = [
        client.get("/api/v1/auth/csrf").json()["csrf_token"]
        for client in (first, second)
    ]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda entry: entry[0].post(
                    "/api/v1/membership/redemptions",
                    json={"code": entry[1]},
                    headers={"Origin": ORIGIN, "X-CSRF-Token": entry[2]},
                ),
                zip((first, second), codes, tokens),
            )
        )
    statuses = sorted(response.status_code for response in results)
    assert statuses in ([200, 401], [200, 403])
    with Session(engine) as db:
        assert (
            len(db.scalars(select(VipCode).where(VipCode.used_by.is_not(None))).all())
            == 1
        )
    second.close()


def test_login_cannot_rotate_a_session_revoked_during_verification(
    environment, monkeypatch
):
    client, engine, _ = environment
    user_id, password = register_login(client)
    original = users.verify_password

    def revoke_before_rotation(encoded, candidate):
        verified = original(encoded, candidate)
        with Session(engine) as db, db.begin():
            db.execute(delete(AuthSession).where(AuthSession.user_id == user_id))
        return verified

    monkeypatch.setattr(users, "verify_password", revoke_before_rotation)
    result = unsafe(
        client,
        "POST",
        "/auth/login",
        {
            "account": "test_user",
            "password": password,
        },
    )
    assert result.status_code == 401
    with Session(engine) as db:
        assert (
            db.scalar(select(AuthSession).where(AuthSession.user_id == user_id)) is None
        )


def test_duplicate_registration_is_unique_under_concurrency(environment):
    first, engine, app = environment
    second = TestClient(app, base_url=ORIGIN)
    password = secrets.token_urlsafe(20)
    payload = {
        "account": "concurrent_user",
        "password": password,
        "confirm_password": password,
    }
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda client: unsafe(client, "POST", "/auth/register", payload),
                [first, second],
            )
        )
    assert sorted(response.status_code for response in results) == [201, 409]
    with Session(engine) as db:
        assert len(db.scalars(select(User)).all()) == 1
    second.close()
