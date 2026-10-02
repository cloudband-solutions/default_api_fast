# 5) Database setup and migrations (Alembic)

Configure the desired environment in [database.yml](../database.yml) first.
The app and Alembic use the same [connection settings and override precedence](step-2-configure-environment.md#26-overrides-and-legacy-configuration).
Run commands from the project root so relative configuration and SQLite paths
resolve consistently. Commands default to `APP_ENV=development`.

With the supplied SQLite configuration, normal development uses
`storage/development.sqlite3`:

```bash
python -m app.cli db:create
python -m app.cli db:upgrade
python -m app.cli server
```

## 5.1 Create the configured database

```bash
python -m app.cli db:create
```

| Adapter | What `db:create` does | Prerequisite |
| --- | --- | --- |
| PostgreSQL | Creates the configured database if it does not exist | Running server; configured role can connect to `postgres` and create databases |
| SQLite file | Creates the file and missing parent directories | Writable database directory |
| SQLite memory | Reports that creation is unnecessary | Schema must be created within the consuming process |

Database creation does not create application tables. Apply migrations next.
Use a file-backed SQLite database for CLI/server workflows: an in-memory database
cannot persist between processes.

## 5.2 Apply migrations

```bash
python -m app.cli db:upgrade
```

To create and migrate `test.sqlite3` for a manual test-environment session:

```bash
APP_ENV=test python -m app.cli db:create
APP_ENV=test python -m app.cli db:upgrade
```

These test-environment commands are not required before running specs. Request
specs create and drop their own tables in `test.sqlite3`. See
[test database setup](step-6-tests.md#test-database-setup).
Use `APP_ENV=production` with these same commands to select production settings.

## 5.3 Generate a new migration from your models

```bash
python -m app.cli db:migrate --message "add projects"
python -m app.cli db:upgrade
```

This starter uses SQLAlchemy 2.0 models with Alembic autogeneration. SQLite
configuration enables batch rendering for generated schema changes. Review
generated migrations before applying them, and verify upgrade and downgrade on
both adapters when maintaining support for both. Changing the configured adapter
does not move data from an existing database.

## 5.4 Roll back migrations

Roll back one revision, inspect history, and show the current revision:

```bash
python -m app.cli db:downgrade
python -m app.cli db:history
python -m app.cli db:current
```

Use `db:upgrade --revision REVISION` or `db:downgrade --revision REVISION` to
target a specific migration revision.
