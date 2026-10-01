import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

LOCAL_DATABASE_URL = "postgresql+psycopg://postgres@127.0.0.1:55479/yupicture"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", LOCAL_DATABASE_URL)


def build_engine(
    *, connect_timeout: int = 2, statement_timeout_ms: int = 2000
) -> Engine:
    return create_engine(
        database_url(),
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": connect_timeout,
            "options": f"-c statement_timeout={statement_timeout_ms}",
        },
    )


def check_database(engine: Engine) -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
