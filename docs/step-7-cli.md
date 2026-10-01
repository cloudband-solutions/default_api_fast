# 7) Command-line routines (`python -m app.cli`)

FastAPI does not ship with a built-in task runner, so this starter exposes a
small Python command runner through `app/cli.py`.

## 7.1 Run a command
```bash
python -m app.cli server
python -m app.cli spec spec/users/test_create.py
python -m app.cli system:seed
python -m app.cli system:restore_factory_settings
python -m app.cli db:create
python -m app.cli db:upgrade
```

`system:seed` creates or updates the default admin user:
- `email`: `admin@example.com`
- `first_name`: `admin`
- `last_name`: `example`
- `role`: `admin`
- `password`: `password`

`system:restore_factory_settings` deletes all application data, then creates a
fresh default admin user:
- `email`: `admin@example.com`
- `first_name`: `Admin`
- `last_name`: `Example`
- `role`: `admin`
- `password`: `password`

Database commands, seeding, and the server use the selected `APP_ENV` section
of `database.yml`, defaulting to `development`. PostgreSQL and SQLite use the
same commands. `DATABASE_URL` overrides the selected section; `DATABASE_YAML`
selects a different configuration file. The `spec` command selects `test`.

For example, create and migrate a file-backed test database:

```bash
APP_ENV=test python -m app.cli db:create
APP_ENV=test python -m app.cli db:upgrade
```

Use file-backed SQLite when separate CLI commands and the server must share
data. See [database setup and migrations](step-5-database-migrations.md) for
adapter-specific prerequisites.

## 7.2 Where tasks live
- `app/cli.py`: command parsing and reusable helpers such as database creation
- `bin/spec`: optional thin wrapper around `python -m app.cli spec`

## 7.3 Template for new commands
```python
def run_seed(_args):
    print("seeded")
```

Then register the handler in `build_parser()` inside `app/cli.py`.
