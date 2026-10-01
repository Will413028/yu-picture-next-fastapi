from alembic import context

from app.database import build_engine
from app.models import Base

target_metadata = Base.metadata


def run_migrations_online() -> None:
    engine = build_engine(connect_timeout=30, statement_timeout_ms=30000)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


run_migrations_online()
