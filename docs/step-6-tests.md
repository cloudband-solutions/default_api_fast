# 6) Specs

This template uses `pytest`, but the project layout and wrapper commands are
set up to feel closer to RSpec:
- specs live in `spec/`
- factories live in `spec/factories.py`
- `./bin/spec` runs the suite
- `./bin/rake spec` is the task-runner equivalent

Run everything:
```bash
./bin/spec
```

Run one file:
```bash
./bin/spec spec/users/test_create.py
```

Filter by keyword:
```bash
./bin/rake spec --keyword create
```

The test app loads `spec.settings.TestConfig`, which defaults to the
`default_api_fast_test` PostgreSQL database.
