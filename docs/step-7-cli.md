# 7) Command-line routines (`bin/rake`)

FastAPI does not ship with a built-in task runner, so this starter uses
`invoke` and wraps it with `bin/rake` to provide namespaced commands.

## 7.1 Run a command
```bash
./bin/rake system.greet
./bin/rake db.create
./bin/rake spec
```

## 7.2 Where tasks live
- `tasks.py`: task definitions and namespaces
- `app/cli.py`: reusable task helpers such as database creation
- `bin/rake`: thin wrapper around `python -m invoke`

## 7.3 Template for new commands
```python
from invoke import task


@task
def seed(ctx):
    ctx.run("python scripts/seed.py", pty=True)
```

Then add it to the root collection in `tasks.py`.
