import os
import shutil
from pathlib import Path

os.environ["APP_ENV"] = "test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import create_app  # noqa: E402
from app.db import Base, db  # noqa: E402
from app.helpers.api_helpers import build_jwt_header, generate_jwt  # noqa: E402
from spec.factories import UserFactory  # noqa: E402


@pytest.fixture()
def app():
    application = create_app("spec.settings.TestConfig")
    Base.metadata.create_all(bind=db.engine)
    yield application
    Base.metadata.drop_all(bind=db.engine)
    storage_root = Path(application.state.settings.STORAGE_LOCAL_ROOT)
    if storage_root.exists():
        shutil.rmtree(storage_root)


@pytest.fixture()
def client(app):
    return TestClient(app)


@pytest.fixture()
def db_session(app):
    session = db.session()
    UserFactory._meta.sqlalchemy_session = session
    yield session
    session.close()
    UserFactory._meta.sqlalchemy_session = None


@pytest.fixture()
def auth_headers(app, db_session):
    user = UserFactory(status="active", role="admin")
    token = generate_jwt(user.to_dict(), app.state.settings.SECRET_KEY)
    return build_jwt_header(token)


@pytest.fixture()
def user_auth_headers(app, db_session):
    user = UserFactory(status="active", role="user")
    token = generate_jwt(user.to_dict(), app.state.settings.SECRET_KEY)
    return build_jwt_header(token)
