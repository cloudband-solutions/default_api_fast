import os
import re
from pathlib import Path

import yaml
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError

from app.environment import load_environment

# Load dotenv before resolving class-level settings, including direct config imports.
load_environment()

_ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


def _expand_env_vars(value):
    if not isinstance(value, str):
        return value

    def _replace(match):
        name = match.group(1)
        if name not in os.environ:
            raise ValueError(f"Database configuration requires environment variable {name}.")
        return os.environ[name]

    return _ENV_PATTERN.sub(_replace, value)


def _load_database_config(env=None):
    explicit_path = os.getenv("DATABASE_YAML")
    config_path = Path(explicit_path or "database.yml")
    if not explicit_path and not config_path.exists():
        config_path = Path("database.yaml")
    if not config_path.is_file():
        raise ValueError(f"Database configuration file not found: {config_path}.")

    try:
        with config_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except (yaml.YAMLError, OSError):
        raise ValueError(f"Cannot read database configuration: {config_path}.") from None

    env = env or os.getenv("APP_ENV", "development")
    if not isinstance(data, dict) or not isinstance(data.get(env), dict):
        raise ValueError(f"Database configuration requires a mapping for environment {env}.")
    return data[env]


def _validate_uri(uri):
    try:
        url = make_url(uri)
        backend = url.get_backend_name()
    except (TypeError, ValueError, ArgumentError):
        raise ValueError("Invalid database URI.") from None
    if backend not in {"postgresql", "sqlite"}:
        raise ValueError("Database adapter must be PostgreSQL or SQLite.")
    if backend == "postgresql" and url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
        return url.render_as_string(hide_password=False)
    return uri


def resolve_database_uri(env=None):
    """Resolve DATABASE_URL, a YAML URI, or structured adapter settings."""
    override = os.getenv("DATABASE_URL")
    if override is not None:
        return _validate_uri(override)

    config = _load_database_config(env)
    if "uri" in config:
        return _validate_uri(_expand_env_vars(config["uri"]))

    config = {key: _expand_env_vars(value) for key, value in config.items()}
    adapter = config.get("adapter")
    if adapter not in ("postgresql", "postgres", "sqlite", "sqlite3"):
        raise ValueError("Database adapter must be PostgreSQL or SQLite.")
    database = config.get("database")
    if not isinstance(database, str) or not database.strip():
        raise ValueError("Database configuration requires a database name or SQLite path.")
    if adapter in ("sqlite", "sqlite3"):
        return URL.create("sqlite", database=database).render_as_string(hide_password=False)

    try:
        raw_port = config.get("port", 5432)
        if isinstance(raw_port, bool) or not isinstance(raw_port, (int, str)):
            raise ValueError
        port = int(raw_port)
        if not 1 <= port <= 65535:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError("PostgreSQL port must be an integer between 1 and 65535.") from None
    for field in ("host", "username", "password"):
        if config.get(field) is not None and not isinstance(config[field], str):
            raise ValueError(f"PostgreSQL {field} must be a string.")
    host = config.get("host", "localhost")
    socket_host = isinstance(host, str) and host.startswith("/")
    return URL.create(
        "postgresql+psycopg",
        database=database,
        host=None if socket_host else host,
        query={"host": host} if socket_host else {},
        port=port,
        username=config.get("username"),
        password=config.get("password"),
    ).render_as_string(hide_password=False)


class Config:
    APP_NAME = os.getenv("APP_NAME", "Default API Fast")
    APP_ENV = os.getenv("APP_ENV", "development")
    API_PREFIX = os.getenv("API_PREFIX", "")

    SQLALCHEMY_DATABASE_URI = resolve_database_uri()
    SECRET_KEY = os.getenv("SECRET_KEY", "default-api-fast-secret")

    STORAGE_SERVICE = os.getenv("STORAGE_SERVICE", "local")
    STORAGE_LOCAL_ROOT = os.getenv("STORAGE_LOCAL_ROOT", str(Path("storage")))
    STORAGE_LOCAL_PUBLIC_ENDPOINT = os.getenv("STORAGE_LOCAL_PUBLIC_ENDPOINT", "/files")
    STORAGE_S3_BUCKET = os.getenv("STORAGE_S3_BUCKET", "")
    STORAGE_S3_REGION = os.getenv("STORAGE_S3_REGION", "")
    STORAGE_S3_ENDPOINT = os.getenv("STORAGE_S3_ENDPOINT", "")
    STORAGE_S3_PREFIX = os.getenv("STORAGE_S3_PREFIX", "")
    STORAGE_S3_PUBLIC_URL = os.getenv("STORAGE_S3_PUBLIC_URL", "")
    STORAGE_S3_PRESIGNED_EXPIRES_IN = int(os.getenv("STORAGE_S3_PRESIGNED_EXPIRES_IN", "3600"))
    STORAGE_S3_ACL = os.getenv("STORAGE_S3_ACL", "")
    STORAGE_MAX_CONTENT_LENGTH_MB = int(os.getenv("STORAGE_MAX_CONTENT_LENGTH_MB", "100"))
