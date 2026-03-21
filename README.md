# FastAPI API Starter

This repository is a FastAPI scaffold that keeps the same high-level shape as
`default_api_flask`: app factory, controller modules, operation objects,
database migrations, storage helpers, and domain-based request specs.

It adds three Rails-style developer affordances by default:
- `spec/` request specs powered by `pytest` and `factory_boy`
- PostgreSQL-first SQLAlchemy + Alembic setup
- namespaced command-line routines through `python -m app.cli`

## High-Level Setup

## 1. Install dependencies
Create a virtual environment and install the project requirements:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## 2. Configure environment variables
Create your local environment file from the template:

```bash
cp .env.example .env
```

By default, the project reads:
- `.env` when `APP_ENV=development`
- `.env.test` when `APP_ENV=test`

Important variables:
- `APP_ENV`: active environment, usually `development` or `test`
- `SECRET_KEY`: JWT signing key
- `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL settings
- `DATABASE_URL`: optional full database URL override
- `STORAGE_*`: local or S3-backed file storage settings

With the default values, the app expects PostgreSQL databases named:
- `default_api_fast_development`
- `default_api_fast_test`

## 3. Create and migrate the database
Create the configured development database:

```bash
python -m app.cli db.create
python -m app.cli db.upgrade
```

Create the test database:

```bash
APP_ENV=test python -m app.cli db.create
APP_ENV=test python -m app.cli db.upgrade
```

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

## 5. Start the development server
Run the local FastAPI server with reload enabled:

```bash
python -m app.cli server
```

This starts Uvicorn on `http://127.0.0.1:3000`.

Useful development endpoints:
- `GET /api/health`
- `POST /api/login`
- `GET /api/users`
- `POST /api/uploads`

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
