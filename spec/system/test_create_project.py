import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_create_project_includes_and_renames_docker_assets(tmp_path):
    target = tmp_path / "sample_service"

    subprocess.run(
        [
            str(PROJECT_ROOT / "bin" / "create_project.sh"),
            str(target),
            "Sample Service",
        ],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert (target / "database.yml").is_file()
    assert not (target / "database.yaml").exists()
    assert (target / "Dockerfile").is_file()
    assert (target / ".dockerignore").is_file()
    compose = (target / "docker-compose.yml").read_text()
    assert "sample-service:latest" in compose
    assert 'container_name: "${CONTAINER_NAME:-sample-service}"' in compose
    assert "default-fast-api" not in compose
    assert not (target / "spec" / "system" / "test_create_project.py").exists()


def test_create_project_includes_database_configuration_and_excludes_sqlite_files(tmp_path):
    source = tmp_path / "template"
    source.mkdir()
    # A minimal source tree keeps the artifact-exclusion test independent of local data.
    (source / "bin").mkdir()
    shutil.copy2(PROJECT_ROOT / "bin" / "create_project.sh", source / "bin")
    (source / ".env.example").write_text("DB_NAME=default_api_fast\n")
    (source / "database.yml").write_text("test:\n  adapter: sqlite\n  database: default_api_fast_test.sqlite3\n")
    for name in ["local.db", "local.sqlite", "local.sqlite3", "local.sqlite3-wal", "local.db-shm", "local.db-journal"]:
        (source / name).write_text("local data")
    target = tmp_path / "sample_service"
    subprocess.run([str(source / "bin" / "create_project.sh"), str(target)], check=True, capture_output=True)
    assert "sample_service_test.sqlite3" in (target / "database.yml").read_text()
    assert not list(target.glob("local.*"))
