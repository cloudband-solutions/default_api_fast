# FastAPI API Starter

This repository is a FastAPI scaffold that keeps the same high-level shape as
`default_api_flask`: app factory, controller modules, operation objects,
database migrations, storage helpers, and domain-based request specs.

It adds three Rails-style developer affordances by default:
- `spec/` request specs powered by `pytest` and `factory_boy`
- PostgreSQL and SQLite support through SQLAlchemy, Alembic, and `database.yml`
- namespaced command-line routines through `python -m app.cli`

## Default Stack

- API framework: `FastAPI`
- ASGI servers: `Uvicorn` for local development, `Gunicorn` with Uvicorn workers for production-style runs
- Database: file-backed SQLite by default, with PostgreSQL and in-memory SQLite support
- ORM and migrations: `SQLAlchemy`, `Alembic`, `psycopg`
- Configuration: `.env` files loaded with `python-dotenv`, plus `database.yml`
- Authentication: JWT tokens with `PyJWT`, password hashing with `Werkzeug`
- File uploads: `python-multipart`
- Storage: local filesystem by default, optional S3-compatible storage through `boto3`
- Local queue development: MiniStack-compatible SQS via `bin/start_ministack.sh`
- Testing: `pytest`, `factory_boy`, `httpx2`
- Project tooling: app-specific CLI commands through `python -m app.cli`

## Quick Start

### Create a New Project

Create a new project from this template:

```bash
bin/create_project.sh ../my_api "My API"
cd ../my_api
```

On Windows, use PowerShell (5.1 or newer):

```powershell
.\bin\create_project.ps1 ..\my_api "My API"
```

Or Command Prompt:

```bat
bin\create_project.bat ..\my_api "My API"
```

Both Windows entry points require Git on `PATH`; the batch file calls the
PowerShell implementation. If script execution is disabled, run
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bin\create_project.ps1 ..\my_api "My API"`.
The display name is optional and defaults to the title-cased directory name.

The generator creates a new directory, includes the `Dockerfile`,
`.dockerignore`, and `docker-compose.yml` assets, removes template-local files,
rewrites application and Docker naming defaults, creates `.env` from
`.env.example`, and initializes a fresh git repository.

### Set Up the Generated Project

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.\env\Scripts\Activate.ps1` in PowerShell or
`env\Scripts\activate.bat` in Command Prompt.

The supplied `database.yml` uses separate file-backed SQLite databases for
development, tests, and the production container:

```yaml
development:
  adapter: sqlite
  database: storage/development.sqlite3
test:
  adapter: sqlite
  database: test.sqlite3
production:
  adapter: sqlite
  database: /data/production.sqlite3
```

For normal development, initialize `storage/development.sqlite3`, seed it, and
start the app. These commands use the `development` section because `APP_ENV`
defaults to `development`:

```bash
python -m app.cli db:create
python -m app.cli db:upgrade
python -m app.cli system:seed
python -m app.cli server
```

For testing, run:

```bash
python -m app.cli spec
```

The spec command selects `APP_ENV=test`, writes to `test.sqlite3`, and creates
and drops the application tables around each test. It never uses
`storage/development.sqlite3`. No separate test migration step is required.

### Deploy on EC2 with persistent SQLite

The Docker image uses `/data/production.sqlite3` in production, and Compose
bind-mounts `${SQLITE_DATA_PATH}` at `/data`. On EC2, point that variable to a
persistent host directory, preferably on EBS:

```bash
sudo mkdir -p /srv/default-api-fast/data
sudo chown 10001:10001 /srv/default-api-fast/data
printf '\nSQLITE_DATA_PATH=/srv/default-api-fast/data\n' >> .env

docker compose build
docker compose run --rm app python -m app.cli db:create
docker compose run --rm app python -m app.cli db:upgrade
docker compose up -d
```

The database remains at
`/srv/default-api-fast/data/production.sqlite3` when the container is rebuilt or
removed. See [the EC2 deployment guide](docs/step-4-gunicorn.md) for permissions,
updates, backups, and SQLite scaling limits.

## High-Level Setup

## 1. Install dependencies
Create a virtual environment and install the project requirements:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## 2. Configure environment variables
If this project was created with a `bin/create_project` script, `.env` has already
been created from `.env.example`. If you are setting up the template repository
itself, create it manually:

```bash
cp .env.example .env
```

By default, the project reads:
- `.env` when `APP_ENV` is unset, `development`, or `production`
- `.env.test` when `APP_ENV=test`

Important variables:
- `APP_ENV`: YAML section to load; defaults to `development`
- `SECRET_KEY`: JWT signing key
- `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL settings
- `DATABASE_URL`: optional full database URL override
- `DATABASE_YAML`: optional configuration file path; defaults to `database.yml`
- `STORAGE_*`: local or S3-backed file storage settings
- `AWS_ENDPOINT`: set to `http://localhost:4566` when developing against MiniStack
- `SQS_QUEUE_URL`: queue URL for the SQS queue your app should use

The default `database.yml` uses SQLite and isolates normal development from
tests and the production container:

```yaml
development:
  adapter: sqlite
  database: storage/development.sqlite3
test:
  adapter: sqlite
  database: test.sqlite3
production:
  adapter: sqlite
  database: /data/production.sqlite3
```

PostgreSQL remains supported. Both adapters use the same database CLI commands.
See [database configuration](docs/step-2-configure-environment.md#25-select-postgresql-or-sqlite)
for test settings, connection overrides, and legacy configuration compatibility.

## 3. Create and migrate the database
Create the configured development database:

```bash
python -m app.cli db:create
python -m app.cli db:upgrade
```

To create or inspect the file-backed test database outside pytest, explicitly
select the test environment:

```bash
APP_ENV=test python -m app.cli db:create
APP_ENV=test python -m app.cli db:upgrade
```

These commands are optional for the spec suite because its fixtures create and
drop the test schema automatically.

## 4. Run specs
Run the full spec suite:

```bash
python -m app.cli spec
```

Run a single spec file:

```bash
python -m app.cli spec spec/users/test_create.py
```

Filter by keyword:

```bash
python -m app.cli spec --keyword create
```

Optional convenience wrapper:

```bash
./bin/spec
./bin/spec spec/users/test_create.py
```

## 5. Seed the default admin
Seed the default admin user for local development:

```bash
python -m app.cli system:seed
```

This creates or updates:
- `email`: `admin@example.com`
- `first_name`: `admin`
- `last_name`: `example`
- `role`: `admin`
- `password`: `password`

## 6. Start the development server
Run the local FastAPI server with reload enabled:

```bash
python -m app.cli server
```

This starts Uvicorn on `http://127.0.0.1:3000`.

If you need local SQS, start MiniStack in a separate terminal:

```bash
bin/start_ministack.sh
```

That script starts MiniStack on `http://localhost:4566`, creates a FIFO queue,
and prints the `AWS_ENDPOINT` and `SQS_QUEUE_URL` values to export into your
shell or `.env`.

Example:

```bash
export AWS_ENDPOINT=http://localhost:4566
export SQS_QUEUE_URL=http://localhost:4566/000000000000/tphlms.fifo
python -m app.cli server
```

Useful development endpoints:
- `GET /health`
- `POST /login`
- `/users` CRUD endpoints require an authenticated admin user
- `POST /uploads`

## Steps
- [1) Create a new project from this codebase](docs/step-1-create-project.md)
- [2) Configure the environment](docs/step-2-configure-environment.md)
- [3) Run the server](docs/step-3-run-server.md)
- [4) Run with Gunicorn](docs/step-4-gunicorn.md)
- [5) Database setup and migrations (Alembic)](docs/step-5-database-migrations.md)
- [6) Specs](docs/step-6-tests.md)
- [7) Command-line routines (`python -m app.cli`)](docs/step-7-cli.md)
- [8) Create a new model (example: Project)](docs/step-8-create-model.md)
- [9) Create a controller (example: Project)](docs/step-9-create-controller.md)
- [10) File uploads (local + S3)](docs/step-10-file-uploads.md)

## Examples
- [Example test stubs](docs/example-test-stubs.md)
- [Controller example](docs/example-controller.md)
