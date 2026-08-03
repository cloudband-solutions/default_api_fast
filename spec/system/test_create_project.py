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

    assert (target / "Dockerfile").is_file()
    assert (target / ".dockerignore").is_file()
    compose = (target / "docker-compose.yml").read_text()
    assert "sample-service:latest" in compose
    assert 'container_name: "${CONTAINER_NAME:-sample-service}"' in compose
    assert "default-fast-api" not in compose
    assert not (target / "spec" / "system" / "test_create_project.py").exists()
