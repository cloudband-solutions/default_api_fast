from types import SimpleNamespace

from app.cli import run_system_seed
from app.helpers.api_helpers import password_match
from app.models.user import User
from spec.factories import UserFactory


def test_system_seed_creates_default_admin_user(app, db_session, capsys, monkeypatch):
    monkeypatch.setattr("app.cli._active_settings", lambda: app.state.settings)

    result = run_system_seed(SimpleNamespace())

    assert result == 0
    db_session.expire_all()
    user = db_session.query(User).filter_by(email="admin@example.com").one()
    assert user.first_name == "admin"
    assert user.last_name == "example"
    assert user.role == "admin"
    assert user.status == "active"
    assert password_match("password", user.password_hash)
    assert capsys.readouterr().out.strip() == "Admin user created: admin@example.com"


def test_system_seed_updates_existing_user_to_default_admin(app, db_session, capsys, monkeypatch):
    monkeypatch.setattr("app.cli._active_settings", lambda: app.state.settings)
    user = db_session.query(User).filter_by(email="admin@example.com").one_or_none()
    if user is None:
        user = UserFactory(
            email="admin@example.com",
            first_name="wrong",
            last_name="name",
            role="user",
            status="inactive",
        )
    else:
        user.first_name = "wrong"
        user.last_name = "name"
        user.role = "user"
        user.status = "inactive"
        db_session.commit()

    result = run_system_seed(SimpleNamespace())

    assert result == 0
    db_session.expire_all()
    user = db_session.query(User).filter_by(email="admin@example.com").one()
    assert user.first_name == "admin"
    assert user.last_name == "example"
    assert user.role == "admin"
    assert user.status == "active"
    assert password_match("password", user.password_hash)
    assert capsys.readouterr().out.strip() == "Admin user updated: admin@example.com"
