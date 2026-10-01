import os
from pathlib import Path

os.environ.setdefault("APP_ENV", "test")

from config import Config, resolve_database_uri  # noqa: E402


class TestConfig(Config):
    APP_ENV = "test"
    SQLALCHEMY_DATABASE_URI = resolve_database_uri("test")
    SECRET_KEY = "test-secret-32-bytes-minimum-key"
    STORAGE_SERVICE = os.getenv("STORAGE_SERVICE", "local")
    STORAGE_LOCAL_ROOT = os.getenv("STORAGE_LOCAL_ROOT", str(Path("storage_test")))
    STORAGE_LOCAL_PUBLIC_ENDPOINT = os.getenv("STORAGE_LOCAL_PUBLIC_ENDPOINT", "/files")
