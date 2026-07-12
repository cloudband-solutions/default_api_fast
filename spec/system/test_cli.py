from types import SimpleNamespace

import pytest

from app.cli import (
    build_parser,
    run_db_create,
    run_db_current,
    run_db_downgrade,
    run_db_history,
    run_db_migrate,
    run_db_upgrade,
    run_greet,
    run_routes,
    run_server,
    run_spec,
    run_system_restore_factory_settings,
    run_system_seed,
    run_users_create_admin,
)
from app.helpers.api_helpers import password_match
from app.models.user import User
from spec.factories import UserFactory


@pytest.mark.parametrize(
    ("argv", "handler"),
    [
        (["server"], run_server),
        (["spec"], run_spec),
        (["system:greet"], run_greet),
        (["system:restore_factory_settings"], run_system_restore_factory_settings),
        (["system:seed"], run_system_seed),
        (["db:create"], run_db_create),
        (["db:migrate"], run_db_migrate),
        (["db:upgrade"], run_db_upgrade),
        (["db:downgrade"], run_db_downgrade),
        (["db:history"], run_db_history),
        (["db:current"], run_db_current),
        (["routes"], run_routes),
        (
            ["users:create-admin", "--email", "admin@example.com", "--password", "password"],
            run_users_create_admin,
        ),
    ],
)
def test_cli_routes_use_colon_namespaces(argv, handler):
    args = build_parser().parse_args(argv)

    assert args.handler is handler


@pytest.mark.parametrize(
    "command",
    [
        "system.greet",
        "db.migrate",
        "db.downgrade",
        "db.history",
        "db.current",
        "users.create-admin",
    ],
)
def test_cli_rejects_dotted_namespaces(command, capsys):
    with pytest.raises(SystemExit) as error:
        build_parser().parse_args([command])

    assert error.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


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


def test_system_restore_factory_settings_clears_database_and_creates_default_admin(
    app, db_session, capsys, monkeypatch
):
    monkeypatch.setattr("app.cli._active_settings", lambda: app.state.settings)
    UserFactory(email="first@example.com")
    UserFactory(email="second@example.com")

    result = run_system_restore_factory_settings(SimpleNamespace())

    assert result == 0
    db_session.expire_all()
    users = db_session.query(User).all()
    assert len(users) == 1
    admin = users[0]
    assert admin.email == "admin@example.com"
    assert admin.first_name == "Admin"
    assert admin.last_name == "Example"
    assert admin.role == "admin"
    assert admin.status == "active"
    assert password_match("password", admin.password_hash)
    assert capsys.readouterr().out.strip() == "Factory settings restored."
