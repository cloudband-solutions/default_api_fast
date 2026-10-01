# 2) Configure the environment

## 2.1 Create your virtual environment
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## 2.2 Create `.env`
Generated projects already include `.env`. If you are setting up this template
repository directly, create it from `.env.example`:

```bash
cp .env.example .env
```

Key settings:
- `APP_ENV`: `development`, `test`, or `production`
- `DATABASE_URL`: optional full override
- `DATABASE_YAML`: optional YAML configuration file path
- `DB_*`: component-based PostgreSQL settings used by `database.yml`
- `SECRET_KEY`: JWT signing key
- `STORAGE_*`: local or S3-backed file storage
- `AWS_ENDPOINT`: point this to `http://localhost:4566` when using MiniStack
- `SQS_QUEUE_URL`: queue URL for the SQS queue the app should use

Set `APP_ENV` in the shell to select an environment before dotenv loading.
The default is `development`. The app loads `.env.test` when `APP_ENV=test`
and `.env` otherwise, including production. Existing shell variables take
precedence over dotenv values. Configure `.env.test` separately for PostgreSQL
tests; changing `.env` does not change the test database settings.

## 2.3 Local SQS with MiniStack
If your development flow uses SQS, start MiniStack in a separate terminal:

```bash
bin/start_ministack.sh
```

The script:
- starts MiniStack on `http://localhost:4566`
- creates a FIFO queue
- prints the `AWS_ENDPOINT` and `SQS_QUEUE_URL` values to export into your shell or save in `.env`

Typical local values look like:

```bash
AWS_ENDPOINT=http://localhost:4566
SQS_QUEUE_URL=http://localhost:4566/000000000000/tphlms.fifo
```

## 2.4 Default database names
The supplied PostgreSQL sections in `database.yml` build database names from `DB_NAME`:
- development: `${DB_NAME}_development`
- test: `${DB_NAME}_test`
- production: `${DB_NAME}`

For example, a generated project named `ragapi` uses:
- development: `ragapi_development`
- test: `ragapi_test`
- production: `ragapi`

## 2.5 Select PostgreSQL or SQLite

`database.yml` has a section for each `APP_ENV`. PostgreSQL is the supplied
default for development, test, and production. Structured PostgreSQL settings:

```yaml
development:
  adapter: postgresql
  database: ${DB_NAME}_development
  host: ${DB_HOST}
  port: ${DB_PORT}
  username: ${DB_USERNAME}
  password: ${DB_PASSWORD}
```

`postgres` is an alias for `postgresql`. The driver is psycopg. When omitted,
`host` defaults to `localhost` and `port` to `5432`; credentials are optional.
The `database` field is required. A Unix-socket directory such as
`host: /var/run/postgresql` is also supported.
Quote literal numeric passwords so YAML reads them as strings. Environment
variables are expanded after parsing, so passwords with URL punctuation work.

To use SQLite, replace the desired environment section:

```yaml
development:
  adapter: sqlite
  database: storage/development.sqlite3
test:
  adapter: sqlite
  database: ":memory:"
```

`sqlite3` is also accepted. SQLite uses Python's built-in driver and needs no
server. Replace the whole section so unused PostgreSQL variables are no longer
referenced. Keep any other environment sections you still use. Paths may be absolute or relative to the working directory. Run
`python -m app.cli db:create` to create the file and its parent directories,
then `python -m app.cli db:upgrade` to apply migrations. In-memory databases
exist only within one process; use file-backed SQLite for separate CLI/server
processes. The test fixtures create the schema for in-memory tests automatically.

## 2.6 Overrides and legacy configuration

The app, CLI, migrations, and specs share this precedence:

1. `DATABASE_URL`, when set, overrides the file entirely.
2. `uri` in the selected YAML section overrides adapter fields.
3. Structured adapter fields build the connection URL.

For example, a URI-based section remains valid:

```yaml
development:
  uri: sqlite:///storage/development.sqlite3
```

PostgreSQL URIs can use `postgresql+psycopg://user:password@localhost:5432/app`.
Plain `postgresql://` URIs also select psycopg. Percent-encode special characters
in URI credentials; structured `username` and `password` fields handle encoding
automatically. YAML strings support `${VARIABLE}` expansion from the environment.

`DATABASE_YAML` selects a custom file, for example:

```bash
DATABASE_YAML=config/databases.yml APP_ENV=production python -m app.cli db:upgrade
```

Without that override, the loader checks `database.yml` in the working directory,
then falls back to `database.yaml` only if `database.yml` is absent. An explicit
`DATABASE_URL` requires no YAML file. Unset `DATABASE_URL` to switch back to YAML;
an empty value is an invalid URL.

Missing configuration files or environments, invalid settings, and references to
unset environment variables raise configuration errors. Restart the process
after changing settings. Switching adapters does not transfer existing data.
