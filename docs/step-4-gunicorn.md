# 4) Deploy on EC2 with Docker, Gunicorn, and SQLite

The image runs Gunicorn as a non-root user and defaults to:

```text
APP_ENV=production
DATABASE_URL=sqlite:////data/production.sqlite3
```

The [`Dockerfile`](../Dockerfile) declares `/data` as a volume. The
[`docker-compose.yml`](../docker-compose.yml) bind-mounts a host directory at
that path, so the SQLite file is not stored in the container's writable layer.
Rebuilding or replacing the container therefore does not replace the database.
Mount the directory rather than only the database file so SQLite journal, WAL,
and shared-memory sidecar files remain on the same persistent filesystem.

## 4.1 Prepare persistent storage on EC2

Use a directory on persistent host storage. For stronger durability, put this
directory on an attached EBS volume rather than the instance's ephemeral disk.
The container runs as UID and GID `10001`, so grant that identity ownership:

```bash
sudo mkdir -p /srv/default-api-fast/data
sudo chown 10001:10001 /srv/default-api-fast/data
sudo chmod 750 /srv/default-api-fast/data
```

Set the bind-mount source in the project's `.env` file on the EC2 host:

```dotenv
SQLITE_DATA_PATH=/srv/default-api-fast/data
HOST_PORT=8081
CONTAINER_NAME=default-fast-api
SECRET_KEY=replace-with-a-long-random-production-secret
```

Do not set `DATABASE_URL` to a development database in this file. Compose
explicitly selects `sqlite:////data/production.sqlite3` inside the container.

## 4.2 Build and initialize the production database

From the checked-out project directory on EC2:

```bash
docker compose build
docker compose run --rm app python -m app.cli db:create
docker compose run --rm app python -m app.cli db:upgrade
docker compose run --rm app python -m app.cli system:seed
```

The first two commands create and migrate:

```text
/srv/default-api-fast/data/production.sqlite3
```

Seeding is optional. Replace the default seeded credentials before exposing the
service.

## 4.3 Start and update the service

Start Gunicorn in the background:

```bash
docker compose up -d
docker compose ps
docker compose logs -f app
```

The supplied port mapping listens on `127.0.0.1:8081` on the EC2 host. Put Nginx
or another TLS reverse proxy in front of it. To deploy a new image while keeping
the same database:

```bash
docker compose build
docker compose run --rm app python -m app.cli db:upgrade
docker compose up -d
```

`docker compose down` removes the container and network but leaves the bind-mounted
SQLite file on the host.

## 4.4 Operational limits and backups

Run one application container against this SQLite file. SQLite is suitable for
modest single-instance workloads, but it is not a shared database for multiple
EC2 instances or containers on different hosts. Use PostgreSQL when horizontal
scaling or sustained concurrent writes are required.

Back up the database to storage outside the container. For example, with the
SQLite CLI installed on the EC2 host:

```bash
sqlite3 /srv/default-api-fast/data/production.sqlite3 \
  ".backup '/srv/default-api-fast/data/production-backup.sqlite3'"
```

Copy backups to a separate durable destination such as S3. Do not copy a live
database file with a plain filesystem copy while writes are in progress.

## 4.5 Run without Docker

For a production-style process directly on a host:

```bash
APP_ENV=production \
DATABASE_URL=sqlite:////srv/default-api-fast/data/production.sqlite3 \
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8081
```
