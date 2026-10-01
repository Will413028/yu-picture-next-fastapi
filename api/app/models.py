from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin', 'vip')", name="user_role"),
        Index("idx_users_name", "name"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    account: Mapped[str] = mapped_column(String(256))
    account_key: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    name: Mapped[str] = mapped_column(String(256), default="無名")
    avatar: Mapped[str | None] = mapped_column(String(1024))
    profile: Mapped[str | None] = mapped_column(String(512))
    role: Mapped[str] = mapped_column(String(16), default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    edited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    vip_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    vip_number: Mapped[int | None] = mapped_column(BigInteger)
    vip_code_id: Mapped[int | None] = mapped_column(
        ForeignKey("vip_codes.id", name="fk_user_vip_code", use_alter=True)
    )


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (Index("idx_sessions_user", "user_id"),)

    token_digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class VipCode(Base):
    __tablename__ = "vip_codes"
    __table_args__ = (
        CheckConstraint("(used_by IS NULL) = (used_at IS NULL)", name="vip_code_usage"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    digest: Mapped[str] = mapped_column(String(64), unique=True)
    used_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
