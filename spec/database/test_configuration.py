from pathlib import Path

import pytest
import yaml
from sqlalchemy.engine import make_url

import config


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_YAML", raising=False)


def write_config(tmp_path, body, name="database.yml"):
    (tmp_path / name).write_text("test:\n" + body)


def test_project_test_environment_uses_dedicated_sqlite_file(monkeypatch):
    project_database_config = Path(__file__).parents[2] / "database.yml"
    monkeypatch.setenv("DATABASE_YAML", str(project_database_config))

    url = make_url(config.resolve_database_uri("test"))

    assert url.get_backend_name() == "sqlite"
    assert url.database == "test.sqlite3"


def test_project_production_environment_uses_container_sqlite_volume(monkeypatch):
    project_database_config = Path(__file__).parents[2] / "database.yml"
    monkeypatch.setenv("DATABASE_YAML", str(project_database_config))

    url = make_url(config.resolve_database_uri("production"))

    assert url.get_backend_name() == "sqlite"
    assert url.database == "/data/production.sqlite3"


def test_postgresql_fields_encode_credentials(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_DB_PASSWORD", "p@ss:/%word")
    write_config(tmp_path, "  adapter: postgresql\n  database: example_test\n  username: user\n  password: ${TEST_DB_PASSWORD}\n")
    url = make_url(config.resolve_database_uri())
    assert url.drivername == "postgresql+psycopg"
    assert url.password == "p@ss:/%word"
    assert (url.host, url.port, url.database) == ("localhost", 5432, "example_test")


@pytest.mark.parametrize("adapter", ["sqlite", "sqlite3"])
@pytest.mark.parametrize("database", [":memory:", "data/test.sqlite3", "/tmp/test.sqlite3"])
def test_sqlite_fields(tmp_path, adapter, database):
    write_config(tmp_path, f"  adapter: {adapter}\n  database: '{database}'\n")
    url = make_url(config.resolve_database_uri())
    assert url.get_backend_name() == "sqlite"
    assert url.database == database


def test_uri_and_environment_override(tmp_path, monkeypatch):
    write_config(tmp_path, "  uri: sqlite:///legacy.db\n  adapter: invalid\n")
    assert config.resolve_database_uri() == "sqlite:///legacy.db"
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    (tmp_path / "database.yml").write_text("invalid: [")
    assert config.resolve_database_uri() == "sqlite:///:memory:"


def test_legacy_file_and_new_file_precedence(tmp_path, monkeypatch):
    write_config(tmp_path, "  uri: sqlite:///legacy.db\n", "database.yaml")
    assert config.resolve_database_uri() == "sqlite:///legacy.db"
    write_config(tmp_path, "  uri: sqlite:///new.db\n")
    assert config.resolve_database_uri() == "sqlite:///new.db"
    monkeypatch.setenv("DATABASE_YAML", str(tmp_path / "database.yaml"))
    assert config.resolve_database_uri() == "sqlite:///legacy.db"


@pytest.mark.parametrize("body", [
    "  adapter: unknown\n  database: test\n",
    "  adapter: sqlite\n",
    "  adapter: sqlite\n  database: ${MISSING_DATABASE_TEST_VARIABLE}\n",
    "  adapter: postgres\n  database: test\n  port: wrong\n",
    "  adapter: [\n",
])
def test_invalid_configuration_fails_without_echoing_values(tmp_path, body):
    write_config(tmp_path, body)
    with pytest.raises(ValueError):
        config.resolve_database_uri()


def test_missing_environment_fails(tmp_path):
    (tmp_path / "database.yml").write_text("production:\n  adapter: sqlite\n  database: prod.db\n")
    with pytest.raises(ValueError, match="test"):
        config.resolve_database_uri()


def test_explicit_environment_and_postgres_alias(tmp_path, monkeypatch):
    (tmp_path / "database.yml").write_text(
        "development:\n  adapter: postgres\n  database: example_development\n"
        "test:\n  adapter: sqlite\n  database: ':memory:'\n"
    )
    monkeypatch.setenv("APP_ENV", "development")
    assert make_url(config.resolve_database_uri()).database == "example_development"
    assert config.resolve_database_uri("test") == "sqlite:///:memory:"


def test_missing_configuration_file(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match="not found"):
        config.resolve_database_uri()
    write_config(tmp_path, "  uri: sqlite:///:memory:\n")
    monkeypatch.setenv("DATABASE_YAML", "missing.yml")
    with pytest.raises(ValueError, match="not found"):
        config.resolve_database_uri()


def test_uri_expansion_and_default_postgresql_driver(tmp_path, monkeypatch):
    monkeypatch.setenv("TEST_DB_HOST", "localhost")
    write_config(tmp_path, "  uri: postgresql://user:pass@${TEST_DB_HOST}/test\n")
    assert config.resolve_database_uri() == "postgresql+psycopg://user:pass@localhost/test"


@pytest.mark.parametrize("uri", ["invalid", "mysql://localhost/test", None, 123])
def test_invalid_uri_is_redacted(tmp_path, uri):
    (tmp_path / "database.yml").write_text(yaml.safe_dump({"test": {"uri": uri}}))
    with pytest.raises(ValueError) as error:
        config.resolve_database_uri()
    assert str(error.value) in {
        "Invalid database URI.", "Database adapter must be PostgreSQL or SQLite."
    }


@pytest.mark.parametrize("port", ["true", "5432.5", "0", "65536"])
def test_invalid_port_types_and_range(tmp_path, port):
    write_config(tmp_path, f"  adapter: postgresql\n  database: test\n  port: {port}\n")
    with pytest.raises(ValueError, match="port"):
        config.resolve_database_uri()


def test_postgresql_socket_host_survives_url_round_trip(tmp_path):
    write_config(tmp_path, "  adapter: postgresql\n  database: test\n  host: /tmp/postgresql\n")
    url = make_url(config.resolve_database_uri())
    assert url.query["host"] == "/tmp/postgresql"
    assert url.database == "test"
