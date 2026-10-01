from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import create_engine, inspect


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_sqlite_migration_round_trip(tmp_path, monkeypatch):
    # The percent character also exercises Alembic's ConfigParser escaping.
    uri = f"sqlite:///{tmp_path / 'migration%test.sqlite3'}"
    monkeypatch.setattr("config.Config.SQLALCHEMY_DATABASE_URI", uri)
    configuration = AlembicConfig(str(PROJECT_ROOT / "alembic.ini"))
    configuration.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    engine = create_engine(uri)
    try:
        command.upgrade(configuration, "head")
        assert "role" in {column["name"] for column in inspect(engine).get_columns("users")}
        command.downgrade(configuration, "base")
        assert "users" not in inspect(engine).get_table_names()
        command.upgrade(configuration, "head")
        assert "users" in inspect(engine).get_table_names()
    finally:
        engine.dispose()
