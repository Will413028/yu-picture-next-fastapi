"""Users, server sessions and atomic membership code redemption."""

import sqlalchemy as sa
from alembic import op

revision = "0002_users"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("account", sa.String(256), nullable=False),
        sa.Column("account_key", sa.Text(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(512), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("avatar", sa.String(1024)),
        sa.Column("profile", sa.String(512)),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.Column("vip_expires_at", sa.DateTime(timezone=True)),
        sa.Column("vip_number", sa.BigInteger()),
        sa.Column("vip_code_id", sa.BigInteger()),
        sa.CheckConstraint("role IN ('user', 'admin', 'vip')", name="user_role"),
    )
    op.create_index("idx_users_name", "users", ["name"])
    op.create_table(
        "auth_sessions",
        sa.Column("token_digest", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("idx_sessions_user", "auth_sessions", ["user_id"])
    op.create_table(
        "vip_codes",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("digest", sa.String(64), nullable=False, unique=True),
        sa.Column("used_by", sa.BigInteger(), sa.ForeignKey("users.id")),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "(used_by IS NULL) = (used_at IS NULL)", name="vip_code_usage"
        ),
    )
    op.create_foreign_key(
        "fk_user_vip_code", "users", "vip_codes", ["vip_code_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_user_vip_code", "users", type_="foreignkey")
    op.drop_table("vip_codes")
    op.drop_table("auth_sessions")
    op.drop_table("users")
