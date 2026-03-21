import os
import shlex

from invoke import Collection, task

from app.cli import create_database, system_greet
from app.environment import load_environment


def _active_settings():
    load_environment()
    from config import Config

    return Config


def _quoted(parts):
    return shlex.join(parts)


@task
def server(ctx, host="127.0.0.1", port=3000, reload=True):
    command = ["uvicorn", "main:app", "--host", host, "--port", str(port)]
    if reload:
        command.append("--reload")
    ctx.run(_quoted(command), pty=True)


@task(help={"target": "Optional file or folder under spec/", "keyword": "pytest -k filter"})
def spec(ctx, target="", keyword=""):
    command = ["pytest", "spec"]
    if target:
        command.append(target)
    if keyword:
        command.extend(["-k", keyword])
    ctx.run(_quoted(command), pty=True, env={"APP_ENV": "test"})


@task
def greet(_ctx):
    system_greet()


@task
def db_create(_ctx):
    create_database(_active_settings())


@task(help={"message": "Migration message"})
def db_migrate(ctx, message="update schema"):
    ctx.run(
        _quoted(["alembic", "revision", "--autogenerate", "-m", message]),
        pty=True,
        env={"APP_ENV": os.getenv("APP_ENV", "development")},
    )


@task(help={"revision": "Alembic revision target"})
def db_upgrade(ctx, revision="head"):
    ctx.run(
        _quoted(["alembic", "upgrade", revision]),
        pty=True,
        env={"APP_ENV": os.getenv("APP_ENV", "development")},
    )


@task(help={"revision": "Alembic revision target"})
def db_downgrade(ctx, revision="-1"):
    ctx.run(
        _quoted(["alembic", "downgrade", revision]),
        pty=True,
        env={"APP_ENV": os.getenv("APP_ENV", "development")},
    )


@task
def db_history(ctx):
    ctx.run("alembic history", pty=True, env={"APP_ENV": os.getenv("APP_ENV", "development")})


@task
def db_current(ctx):
    ctx.run("alembic current", pty=True, env={"APP_ENV": os.getenv("APP_ENV", "development")})


@task
def routes(_ctx):
    settings = _active_settings()
    print(f"Mounted API prefix: {settings.API_PREFIX}")
    print("Routes: /health, /login, /users, /uploads, /files/{key}")


ns = Collection()
ns.add_task(server, "server")
ns.add_task(spec, "spec")

system = Collection("system")
system.add_task(greet, "greet")
ns.add_collection(system)

database = Collection("db")
database.add_task(db_create, "create")
database.add_task(db_migrate, "migrate")
database.add_task(db_upgrade, "upgrade")
database.add_task(db_downgrade, "downgrade")
database.add_task(db_history, "history")
database.add_task(db_current, "current")
ns.add_collection(database)

ns.add_task(routes, "routes")
