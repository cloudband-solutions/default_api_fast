from pathlib import Path

from sqlalchemy.engine import make_url


def test_test_environment_is_isolated_from_development(app):
    database_url = make_url(app.state.settings.SQLALCHEMY_DATABASE_URI)

    assert database_url.database == "test.sqlite3"
    assert Path(app.state.settings.STORAGE_LOCAL_ROOT) == Path("storage_test")
