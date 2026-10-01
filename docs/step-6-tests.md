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

### PostgreSQL (default)

Configure `DB_*` in `.env.test`, start PostgreSQL, and create the test database:

```bash
APP_ENV=test python -m app.cli db:create
python -m app.cli spec
```

The supplied configuration names it `${DB_NAME}_test`; a generated project named
`ragapi` uses `ragapi_test`. Request fixtures create and drop application tables,
so running migrations first is optional for these specs.

### SQLite

For an in-memory database without editing configuration:

```bash
DATABASE_URL=sqlite:///:memory: python -m app.cli spec
```

Or replace the `test` section in `database.yml`:

```yaml
test:
  adapter: sqlite
  database: ":memory:"
```

Then run `python -m app.cli spec`. No `db:create` or migration command is needed.
The in-memory connection is shared across request threads within the test
process, and request fixtures create and drop tables for each test.

For file-backed SQLite, set `test.database` to `tmp/spec.sqlite3`, then run:

```bash
APP_ENV=test python -m app.cli db:create
python -m app.cli spec
```

Keep test database files outside the configured local upload-storage directory,
which request fixtures remove during cleanup. SQLite database files and sidecars
are excluded from Git, Docker build context, and generated projects.

Use a dedicated test database: request fixtures drop application tables after
each test. An exported `DATABASE_URL` still overrides the test section, so ensure
it points to the test database or unset it before running specs.
