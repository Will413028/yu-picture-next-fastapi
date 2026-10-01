import hashlib
import hmac
import os
import secrets
import unicodedata
from datetime import UTC, datetime, timedelta
from typing import Annotated

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import AuthSession, User

COOKIE_NAME = "yu_session"
HASHER = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)
DUMMY_HASH = HASHER.hash(secrets.token_urlsafe(32))


def now() -> datetime:
    return datetime.now(UTC)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def account_key(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


def verify_password(encoded: str, password: str) -> bool:
    try:
        return HASHER.verify(encoded, password)
    except (VerificationError, InvalidHashError):
        return False


def get_db(request: Request):
    with Session(request.app.state.engine) as db, db.begin():
        yield db
        token_digest = db.info.get("touch")
        if token_digest:
            db.execute(
                update(AuthSession)
                .where(AuthSession.token_digest == token_digest)
                .values(last_seen_at=now())
            )


Database = Annotated[Session, Depends(get_db, scope="function")]


def session_for_request(request: Request, db: Session) -> AuthSession | None:
    token = request.cookies.get(COOKIE_NAME, "")
    if not 32 <= len(token) <= 128:
        return None
    row = db.get(AuthSession, digest(token))
    timestamp = now()
    if row is None or timestamp >= row.created_at + timedelta(hours=24):
        return None
    if timestamp >= row.last_seen_at + timedelta(minutes=30):
        return None
    db.info["touch"] = row.token_digest
    return row


def csrf_for_token(token: str) -> str:
    return hmac.new(token.encode(), b"yu-picture:csrf", hashlib.sha256).hexdigest()


def issue_session(db: Session, response: Response, user_id: int | None) -> str:
    token = secrets.token_urlsafe(32)
    timestamp = now()
    db.add(
        AuthSession(
            token_digest=digest(token),
            user_id=user_id,
            created_at=timestamp,
            last_seen_at=timestamp,
        )
    )
    db.info["touch"] = digest(token)
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        path="/",
        secure=os.environ.get("APP_ENV") != "local",
        max_age=86400,
    )
    return token


def require_csrf(request: Request, db: Database) -> AuthSession:
    default_origin = (
        "http://127.0.0.1:3309" if os.environ.get("APP_ENV") == "local" else ""
    )
    origins = set(os.environ.get("ALLOWED_ORIGINS", default_origin).split(",")) - {""}
    if request.headers.get("origin") not in origins:
        raise HTTPException(403, "請求來源不被允許")
    row = session_for_request(request, db)
    token = request.cookies.get(COOKIE_NAME, "")
    if row is None or not hmac.compare_digest(
        request.headers.get("x-csrf-token", "").encode(),
        csrf_for_token(token).encode("ascii"),
    ):
        raise HTTPException(403, "安全驗證失敗，請重新整理")
    return row


def require_user(request: Request, db: Database) -> User:
    row = session_for_request(request, db)
    user = db.get(User, row.user_id) if row and row.user_id else None
    if user is None or user.is_deleted:
        raise HTTPException(401, "請先登入")
    return user


CurrentUser = Annotated[User, Depends(require_user)]


def require_admin(user: CurrentUser) -> User:
    if user.role != "admin":
        raise HTTPException(403, "需要管理員權限")
    return user


AdminUser = Annotated[User, Depends(require_admin)]
