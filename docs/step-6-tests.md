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

The test app loads `spec.settings.TestConfig`, which defaults to the
`default_api_fast_test` PostgreSQL database.
