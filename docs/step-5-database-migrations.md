# 5) Database setup and migrations (Alembic)

## 5.1 Create the configured database
```bash
./bin/rake db.create
```

For the test database:
```bash
APP_ENV=test ./bin/rake db.create
```

## 5.2 Apply migrations
```bash
./bin/rake db.upgrade
```

## 5.3 Generate a new migration from your models
```bash
./bin/rake db.migrate --message "add projects"
./bin/rake db.upgrade
```

## 5.4 Roll back migrations
```bash
./bin/rake db.downgrade
./bin/rake db.history
./bin/rake db.current
```

This starter uses SQLAlchemy 2.0 models with Alembic autogeneration. The
database URL comes from `DATABASE_URL` or the active section in `database.yaml`.
