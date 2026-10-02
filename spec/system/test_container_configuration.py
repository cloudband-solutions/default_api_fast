from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).parents[2]


def test_docker_image_uses_external_production_sqlite_volume():
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text()

    assert "APP_ENV=production" in dockerfile
    assert "DATABASE_URL=sqlite:////data/production.sqlite3" in dockerfile
    assert 'VOLUME ["/data"]' in dockerfile


def test_compose_bind_mounts_the_production_sqlite_directory():
    compose = yaml.safe_load((PROJECT_ROOT / "docker-compose.yml").read_text())
    app = compose["services"]["app"]

    assert app["environment"]["APP_ENV"] == "production"
    assert app["environment"]["DATABASE_URL"] == "sqlite:////data/production.sqlite3"
    assert "${SQLITE_DATA_PATH:-./data}:/data" in app["volumes"]
