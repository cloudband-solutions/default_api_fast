from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from sqlalchemy import text

from app.cli import create_database
from app.db import DatabaseManager


def test_memory_database_shared_between_threads():
    manager = DatabaseManager()
    manager.configure("sqlite:///:memory:")
    try:
        with manager.engine.begin() as connection:
            connection.execute(text("CREATE TABLE probe (value INTEGER)"))
            connection.execute(text("INSERT INTO probe VALUES (42)"))

        def read():
            with manager.session() as session:
                return session.execute(text("SELECT value FROM probe")).scalar_one()

        with ThreadPoolExecutor(max_workers=1) as executor:
            assert executor.submit(read).result() == 42
    finally:
        manager.engine.dispose()


def test_create_sqlite_database_with_parent_directory(tmp_path):
    path = tmp_path / "nested" / "test.sqlite3"
    create_database(SimpleNamespace(SQLALCHEMY_DATABASE_URI=f"sqlite:///{path}"))
    assert path.is_file()


def test_reconfiguring_same_database_preserves_in_memory_data():
    manager = DatabaseManager()
    manager.configure("sqlite:///:memory:")
    try:
        with manager.engine.begin() as connection:
            connection.execute(text("CREATE TABLE probe (value INTEGER)"))
        manager.configure("sqlite:///:memory:")
        with manager.session() as session:
            session.execute(text("SELECT * FROM probe"))
    finally:
        manager.engine.dispose()
