# 6) Specs

This template uses `pytest`, but the project layout and wrapper commands are
set up to feel closer to RSpec:
- specs live in `spec/`
- factories live in `spec/factories.py`
- `python -m app.cli spec` is the primary test command
- `./bin/spec` is an optional thin wrapper around it

Run everything:
```bash
python -m app.cli spec
```

Run one file:
```bash
python -m app.cli spec spec/users/test_create.py
```

Filter by keyword:
```bash
python -m app.cli spec --keyword create
```

Optional wrapper:
```bash
./bin/spec
./bin/spec spec/users/test_create.py
```

## Test database setup

`python -m app.cli spec` sets `APP_ENV=test`. The test app loads
`spec.settings.TestConfig`, using the `test` section of `database.yml` and variables
from `.env.test`. `DATABASE_URL` overrides that section, and `DATABASE_YAML`
selects a custom file, just as for the app and CLI.

### SQLite (default)

The supplied configuration uses a dedicated file outside the development
storage directory:

```yaml
test:
  adapter: sqlite
  database: test.sqlite3
```

Run the suite directly:

```bash
python -m app.cli spec
```

The command sets `APP_ENV=test`. SQLite creates `test.sqlite3` as needed, and
request fixtures create and drop its application tables around each test. The
file remains after the suite and is ignored by Git. No `db:create` or migration
command is required.

Keep test database files outside the local upload-storage directory. Test
uploads use `storage_test/`, which fixtures remove during cleanup; development
uploads and `storage/development.sqlite3` remain under `storage/`.

For an in-memory database without editing configuration:

```bash
DATABASE_URL=sqlite:///:memory: python -m app.cli spec
```

The in-memory connection is shared across request threads within the test
process, and request fixtures create and drop tables for each test.

### PostgreSQL

To test with PostgreSQL instead, replace the `test` section, configure `DB_*`
in `.env.test`, start PostgreSQL, and create the database:

```bash
APP_ENV=test python -m app.cli db:create
python -m app.cli spec
```

Use a dedicated test database: request fixtures drop application tables after
each test. An exported `DATABASE_URL` still overrides the test section, so ensure
it points to the test database or unset it before running specs.
