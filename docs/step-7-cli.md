# 7) Command-line routines (`python -m app.cli`)

FastAPI does not ship with a built-in task runner, so this starter exposes a
small Python command runner through `app/cli.py`.

## 7.1 Run a command
```bash
python -m app.cli server
python -m app.cli spec spec/users/test_create.py
python -m app.cli system.greet
python -m app.cli db.create
python -m app.cli db.upgrade
```

## 7.2 Where tasks live
- `app/cli.py`: command parsing and reusable helpers such as database creation
- `bin/spec`: optional thin wrapper around `python -m app.cli spec`

## 7.3 Template for new commands
```python
import subprocess


def run_seed(_args):
    subprocess.run(["python", "scripts/seed.py"], check=False)
```

Then register the handler in `build_parser()` inside `app/cli.py`.
