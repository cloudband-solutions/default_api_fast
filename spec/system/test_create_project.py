import os
import shutil
import subprocess
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(params=["sh", "ps1", "bat"])
def generator(request):
    extension = request.param
    script = PROJECT_ROOT / "bin" / f"create_project.{extension}"
    assert script.is_file()
    if extension == "sh":
        if not shutil.which("bash"):
            pytest.skip("Bash is not installed")
        prefix = ["bash"]
    elif extension == "ps1":
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            pytest.skip("PowerShell is not installed")
        prefix = [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File"]
    else:
        if os.name != "nt":
            pytest.skip("Batch scripts require Windows")
        prefix = ["cmd.exe", "/d", "/c"]

    def run(*args, source=PROJECT_ROOT):
        return subprocess.run(
            [*prefix, str(source / "bin" / script.name), *map(str, args)],
            cwd=source, capture_output=True, text=True,
        )

    return run


def test_create_project_includes_and_renames_docker_assets(tmp_path, generator):
    target = tmp_path / "sample_service"

    result = generator(target, "Sample Service")
    assert result.returncode == 0, result.stderr

    assert (target / "database.yml").is_file()
    assert not (target / "database.yaml").exists()
    assert (target / "Dockerfile").is_file()
    assert (target / ".dockerignore").is_file()
    compose = (target / "docker-compose.yml").read_text()
    assert "sample-service:latest" in compose
    assert 'container_name: "${CONTAINER_NAME:-sample-service}"' in compose
    assert "default-fast-api" not in compose
    assert not (target / "spec" / "system" / "test_create_project.py").exists()
    assert not list((target / "bin").glob("create_project.*"))
    assert (target / ".env").read_bytes() == (target / ".env.example").read_bytes()
    assert (target / ".git").is_dir()


def test_create_project_includes_database_configuration_and_excludes_sqlite_files(tmp_path, generator):
    source = tmp_path / "template"
    source.mkdir()
    # A minimal source tree keeps the artifact-exclusion test independent of local data.
    (source / "bin").mkdir()
    for script in (PROJECT_ROOT / "bin").glob("create_project.*"):
        shutil.copy2(script, source / "bin")
    (source / ".env.example").write_text("DB_NAME=default_api_fast\n")
    (source / "database.yml").write_text("test:\n  adapter: sqlite\n  database: default_api_fast_test.sqlite3\n")
    for name in ["local.db", "local.sqlite", "local.sqlite3", "local.sqlite3-wal", "local.db-shm", "local.db-journal"]:
        (source / name).write_text("local data")
    target = tmp_path / "sample_service"
    result = generator(target, source=source)
    assert result.returncode == 0, result.stderr
    assert "sample_service_test.sqlite3" in (target / "database.yml").read_text()
    assert not list(target.glob("local.*"))


def test_create_project_preserves_binary_and_literal_display_name(tmp_path, generator):
    source = tmp_path / "template with spaces"
    (source / "bin").mkdir(parents=True)
    for script in (PROJECT_ROOT / "bin").glob("create_project.*"):
        shutil.copy2(script, source / "bin")
    (source / ".env.example").write_text("default_api_fast\ndefault-api-fast-secret\n")
    (source / "title.txt").write_text("Default API Fast\ndefault-fast-api\n")
    binary = b"\x00\xffdefault_api_fast"
    (source / "image.bin").write_bytes(binary)
    for name in [".git", "env", "venv", ".venv", "__pycache__", ".pytest_cache", "storage", "storage_test", "htmlcov"]:
        (source / name).mkdir()
        (source / name / "local.txt").write_text("private")
    (source / ".env").write_text("private")
    (source / ".env.local").write_text("private")
    (source / ".coverage").write_text("private")
    target = tmp_path / "My-Service Name"
    result = generator(target, "API $1 & Team", source=source)
    assert result.returncode == 0, result.stderr
    assert (target / "title.txt").read_text() == "API $1 & Team\nmy-service-name\n"
    assert (target / ".env").read_text() == "my_service_name\nmy_service_name-secret\n"
    assert (target / "image.bin").read_bytes() == binary
    assert not list(target.rglob("local.txt"))
    assert not (target / ".env.local").exists()
    assert not (target / ".coverage").exists()


def test_create_project_derives_display_name(tmp_path, generator):
    result = generator(tmp_path / "my-service")
    assert result.returncode == 0, result.stderr
    assert "Created My Service at" in result.stdout


def test_create_project_rejects_existing_target(tmp_path, generator):
    target = tmp_path / "existing"
    target.mkdir()
    (target / "keep.txt").write_text("keep")
    result = generator(target)
    assert result.returncode != 0
    assert "Target already exists" in result.stderr
    assert (target / "keep.txt").read_text() == "keep"


@pytest.mark.parametrize("name", ["123-service", "---"])
def test_create_project_rejects_invalid_names(tmp_path, generator, name):
    target = tmp_path / name
    result = generator(target)
    assert result.returncode != 0
    assert "valid snake_case project name" in result.stderr
    assert not target.exists()


@pytest.mark.parametrize("args,code", [([], 1), (["--help"], 0), (["-h"], 0), (["one", "two", "three"], 1)])
def test_create_project_usage(generator, args, code):
    result = generator(*args)
    assert result.returncode == code
    assert "Usage:" in result.stdout + result.stderr
