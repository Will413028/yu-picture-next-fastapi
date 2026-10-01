import calendar
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AuthSession, User, VipCode
from app.security import (
    COOKIE_NAME,
    DUMMY_HASH,
    HASHER,
    AdminUser,
    CurrentUser,
    Database,
    account_key,
    csrf_for_token,
    digest,
    issue_session,
    now,
    require_csrf,
    session_for_request,
    verify_password,
)
from app.user_schemas import (
    CreatedUser,
    Credentials,
    CsrfView,
    PublicUser,
    Redemption,
    Registration,
    UserCreate,
    UserPage,
    UserUpdate,
    UserView,
)

router = APIRouter(prefix="/api/v1")
CSRF = Annotated[AuthSession, Depends(require_csrf)]


def public_profile(user: User) -> dict:
    return {
        "id": str(user.id),
        "name": user.name,
        "avatar": user.avatar,
        "profile": user.profile,
        "created_at": user.created_at,
    }


def user_view(user: User) -> dict:
    return {
        **public_profile(user),
        "account": user.account,
        "role": user.role,
        "edited_at": user.edited_at,
        "updated_at": user.updated_at,
        "vip_expires_at": user.vip_expires_at,
        "vip_number": str(user.vip_number) if user.vip_number is not None else None,
    }


def active_user(db: Session, user_id: int, *, lock: bool = False) -> User:
    query = select(User).where(User.id == user_id, User.is_deleted.is_(False))
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    user = db.scalar(query)
    if user is None:
        raise HTTPException(404, "找不到使用者")
    return user


def create_user(db: Session, payload: Credentials, **fields) -> User:
    timestamp = now()
    user = User(
        account=payload.account,
        account_key=account_key(payload.account),
        password_hash=HASHER.hash(payload.password),
        created_at=timestamp,
        updated_at=timestamp,
        edited_at=timestamp,
        **fields,
    )
    db.add(user)
    try:
        db.flush()
    except IntegrityError:
        raise HTTPException(409, "帳號已存在") from None
    return user


def revoke_sessions(db: Session, user_id: int) -> None:
    db.execute(delete(AuthSession).where(AuthSession.user_id == user_id))


@router.get("/auth/csrf", response_model=CsrfView)
def csrf(request: Request, response: Response, db: Database):
    row = session_for_request(request, db)
    if row is None:
        token = issue_session(db, response, None)
    else:
        token = request.cookies[COOKIE_NAME]
    response.headers["Cache-Control"] = "no-store"
    return {"csrf_token": csrf_for_token(token)}


@router.post("/auth/register", status_code=201, response_model=CreatedUser)
def register(payload: Registration, db: Database, csrf: CSRF):
    user = create_user(db, payload, role="user", name="無名")
    return {"id": str(user.id)}


@router.post("/auth/login", response_model=UserView)
def login(payload: Credentials, response: Response, db: Database, csrf: CSRF):
    user = db.scalar(
        select(User)
        .where(
            User.account_key == account_key(payload.account), User.is_deleted.is_(False)
        )
        .with_for_update()
    )
    verified = verify_password(
        user.password_hash if user else DUMMY_HASH, payload.password
    )
    if not user or not verified:
        raise HTTPException(401, "帳號或密碼錯誤")
    if db.get(AuthSession, csrf.token_digest, populate_existing=True) is None:
        raise HTTPException(401, "登入已失效，請重新登入")
    if HASHER.check_needs_rehash(user.password_hash):
        user.password_hash = HASHER.hash(payload.password)
    db.delete(csrf)
    issue_session(db, response, user.id)
    response.headers["Cache-Control"] = "no-store"
    return user_view(user)


@router.get("/auth/me", response_model=UserView)
def me(response: Response, user: CurrentUser):
    response.headers["Cache-Control"] = "no-store"
    return user_view(user)


@router.post("/auth/logout", status_code=204)
def logout(response: Response, db: Database, user: CurrentUser, csrf: CSRF):
    db.delete(csrf)
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/users/{user_id}", response_model=PublicUser)
def profile(user_id: int, db: Database):
    return public_profile(active_user(db, user_id))


@router.get("/admin/users", response_model=UserPage)
def list_users(
    response: Response,
    db: Database,
    admin: AdminUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    id: int | None = Query(None, gt=0),
    account: str | None = None,
    name: str | None = None,
    profile: str | None = None,
    role: str | None = Query(None, pattern="^(user|admin|vip)$"),
    sort: str = Query(
        "created_at", pattern="^(id|account|name|role|created_at|updated_at)$"
    ),
    direction: str = Query("desc", pattern="^(asc|desc)$"),
):
    response.headers["Cache-Control"] = "no-store"
    filters = [User.is_deleted.is_(False)]
    if id is not None:
        filters.append(User.id == id)
    for value, column in (
        (account, User.account),
        (name, User.name),
        (profile, User.profile),
    ):
        if value is not None:
            filters.append(column.icontains(value, autoescape=True))
    if role:
        filters.append(User.role == role)
    column = getattr(User, sort)
    ordering = column.asc() if direction == "asc" else column.desc()
    users = db.scalars(
        select(User)
        .where(*filters)
        .order_by(ordering, User.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    total = db.scalar(select(func.count()).select_from(User).where(*filters))
    return {
        "items": [user_view(user) for user in users],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/admin/users", status_code=201, response_model=UserView)
def add_user(payload: UserCreate, db: Database, admin: AdminUser, csrf: CSRF):
    fields = payload.model_dump(exclude={"account", "password"})
    return user_view(create_user(db, payload, **fields))


@router.get("/admin/users/{user_id}", response_model=UserView)
def get_user(user_id: int, response: Response, db: Database, admin: AdminUser):
    response.headers["Cache-Control"] = "no-store"
    return user_view(active_user(db, user_id))


@router.patch("/admin/users/{user_id}", response_model=UserView)
def update_user(
    user_id: int, payload: UserUpdate, db: Database, admin: AdminUser, csrf: CSRF
):
    user = active_user(db, user_id, lock=True)
    fields = payload.model_dump(exclude_unset=True)
    if "role" in fields and fields["role"] != user.role:
        revoke_sessions(db, user.id)
    for field, value in fields.items():
        setattr(user, field, value)
    user.updated_at = user.edited_at = now()
    db.flush()
    return user_view(user)


@router.delete("/admin/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Database, admin: AdminUser, csrf: CSRF):
    user = active_user(db, user_id, lock=True)
    user.is_deleted = True
    user.updated_at = now()
    revoke_sessions(db, user.id)


def apply_membership(user: User, code: VipCode, timestamp: datetime) -> None:
    day = min(
        timestamp.day, calendar.monthrange(timestamp.year + 1, timestamp.month)[1]
    )
    user.vip_expires_at = timestamp.replace(year=timestamp.year + 1, day=day)
    user.vip_code_id = code.id
    user.role = "vip"
    user.updated_at = timestamp


@router.post("/membership/redemptions", response_model=UserView)
def redeem(
    payload: Redemption,
    request: Request,
    response: Response,
    db: Database,
    current: CurrentUser,
    csrf: CSRF,
):
    user = active_user(db, current.id, lock=True)
    if db.get(AuthSession, csrf.token_digest, populate_existing=True) is None:
        raise HTTPException(401, "登入已失效")
    code = db.scalar(
        select(VipCode).where(VipCode.digest == digest(payload.code)).with_for_update()
    )
    if code is None or code.used_by is not None:
        raise HTTPException(409, "兌換碼無效或已使用")
    timestamp = now()
    code.used_by, code.used_at = user.id, timestamp
    apply_membership(user, code, timestamp)
    revoke_sessions(db, user.id)
    issue_session(db, response, user.id)
    db.flush()
    response.headers["Cache-Control"] = "no-store"
    return user_view(user)
