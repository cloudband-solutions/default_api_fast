# 1) Create a new project from this codebase

## 1.1 Generate the project
Run this from the template repository:

```bash
bin/create_project.sh /home/ralampay/workspace/cloudband/ragapi "RAG API"
cd /home/ralampay/workspace/cloudband/ragapi
```

On Windows, use `.\bin\create_project.ps1 ..\ragapi "RAG API"` in PowerShell,
or `bin\create_project.bat ..\ragapi "RAG API"` in Command Prompt, then
`cd ..\ragapi`. Both require Git on `PATH` and PowerShell 5.1 or newer.
If PowerShell blocks script execution, invoke it with
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\bin\create_project.ps1 ..\ragapi "RAG API"`.

The generator copies this template, including `Dockerfile`, `.dockerignore`, and
`docker-compose.yml` and `database.yml`; excludes local SQLite databases and
sidecars; removes local-only files; creates `.env` from
`.env.example`; initializes a fresh git repository; and replaces:
- `default_api_fast` with the new snake_case project name
- `default-api-fast-secret` with the new default secret
- `Default API Fast` with the display name
- Docker image, container, extension, and anchor names with the kebab-case
  project name (for example, `ragapi` or `my-api`)

If the display name is omitted, the generator derives one from the target
directory name:

```bash
bin/create_project.sh ../ragapi
```

## 1.2 Install and verify
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

On Windows, replace the activation command with `.\env\Scripts\Activate.ps1`
in PowerShell or `env\Scripts\activate.bat` in Command Prompt.

The supplied [`database.yml`](../database.yml) uses SQLite with
`storage/development.sqlite3` for normal development and `test.sqlite3` for
tests. See [Configure PostgreSQL or SQLite](step-2-configure-environment.md#25-select-postgresql-or-sqlite)
if you need a different adapter.

Initialize the development database:

```bash
python -m app.cli db:create
python -m app.cli db:upgrade
python -m app.cli system:seed
```

Then verify with the isolated SQLite test database:

```bash
python -m app.cli spec
```

The spec command selects the `test` section automatically. Its fixtures create
and drop tables in `test.sqlite3`, so no separate test database or migration
command is required.

## 1.3 Create the initial commit
```bash
git add .
git commit -m "Initial commit"
```
