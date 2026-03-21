from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def system_greet():
    print("hello world")


def _quote_identifier(name):
    return f"\"{name.replace('\"', '\"\"')}\""


def _ensure_sqlite_db(database_path):
    if not database_path or database_path == ":memory:":
        print("SQLite in-memory database does not need creation.")
        return

    path = Path(database_path)
    if not path.is_absolute():
        path = Path.cwd() / path

    path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{path}")
    engine.connect().close()
    print(f"SQLite database ready at {path}")


def create_database(settings):
    database_uri = settings.SQLALCHEMY_DATABASE_URI
    if not database_uri:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is not configured.")

    url = make_url(database_uri)
    if url.get_backend_name() == "sqlite":
        _ensure_sqlite_db(url.database)
        return

    db_name = url.database
    if not db_name:
        raise RuntimeError("Database name is missing from SQLALCHEMY_DATABASE_URI.")

    try:
        admin_url = url.set(database="postgres")
    except AttributeError:
        admin_url = url._replace(database="postgres")

    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if exists:
            print(f"Database already exists: {db_name}")
            return

        connection.execute(text(f"CREATE DATABASE {_quote_identifier(db_name)}"))
        print(f"Database created: {db_name}")
