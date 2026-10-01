from sqlalchemy import text

from app.database import build_engine


def test_database_is_at_expected_migration_revision():
    engine = build_engine()
    try:
        with engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
        assert revision == "0002_users"
    finally:
        engine.dispose()
