#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bin/create_project.sh TARGET_DIR [DISPLAY_NAME]

Examples:
  bin/create_project.sh ../ragapi
  bin/create_project.sh ../ragapi "RAG API"
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage >&2
  exit 1
fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="$1"
TARGET_PARENT="$(dirname "${TARGET_DIR}")"
TARGET_BASENAME="$(basename "${TARGET_DIR}")"

mkdir -p "${TARGET_PARENT}"
TARGET_PARENT="$(cd "${TARGET_PARENT}" && pwd)"
TARGET_DIR="${TARGET_PARENT}/${TARGET_BASENAME}"

if [[ -e "${TARGET_DIR}" ]]; then
  printf 'Target already exists: %s\n' "${TARGET_DIR}" >&2
  exit 1
fi

if ! command -v perl >/dev/null 2>&1; then
  printf 'This script requires perl for safe project-name replacement.\n' >&2
  exit 1
fi

project_slug="$(
  printf '%s' "${TARGET_BASENAME}" |
    tr '[:upper:]-' '[:lower:]_' |
    sed -E 's/[^a-z0-9_]+/_/g; s/^_+//; s/_+$//; s/_+/_/g'
)"

if [[ -z "${project_slug}" || ! "${project_slug}" =~ ^[a-z][a-z0-9_]*$ ]]; then
  printf 'Target directory name must produce a valid snake_case project name: %s\n' "${TARGET_BASENAME}" >&2
  exit 1
fi

display_name="${2:-$(
  printf '%s' "${project_slug}" |
    awk -F_ '{ for (i = 1; i <= NF; i++) { printf "%s%s", toupper(substr($i, 1, 1)) substr($i, 2), (i < NF ? " " : "") } }'
)}"
docker_name="${project_slug//_/-}"

mkdir "${TARGET_DIR}"

(
  cd "${SOURCE_DIR}"
  tar \
    --exclude='./.git' \
    --exclude='*.db' \
    --exclude='*.sqlite' \
    --exclude='*.sqlite3' \
    --exclude='*.db-*' \
    --exclude='*.sqlite-*' \
    --exclude='*.sqlite3-*' \
    --exclude='./.env' \
    --exclude='./.env.local' \
    --exclude='./env' \
    --exclude='./venv' \
    --exclude='./.venv' \
    --exclude='./ENV' \
    --exclude='./__pycache__' \
    --exclude='./.pytest_cache' \
    --exclude='./storage' \
    --exclude='./storage_test' \
    --exclude='./htmlcov' \
    --exclude='./.coverage' \
    --exclude='./bin/create_project.sh' \
    --exclude='./bin/create_project.ps1' \
    --exclude='./bin/create_project.bat' \
    --exclude='./spec/system/test_create_project.py' \
    -cf - .
) | (
  cd "${TARGET_DIR}"
  tar -xf -
)

export TEMPLATE_SNAKE="default_api_fast"
export TEMPLATE_SECRET="default-api-fast-secret"
export TEMPLATE_TITLE="Default API Fast"
export TEMPLATE_DOCKER_NAME="default-fast-api"
export PROJECT_SNAKE="${project_slug}"
export PROJECT_SECRET="${project_slug}-secret"
export PROJECT_TITLE="${display_name}"
export PROJECT_DOCKER_NAME="${docker_name}"

find "${TARGET_DIR}" -type f \
  ! -path '*/.git/*' \
  ! -path '*/env/*' \
  ! -path '*/venv/*' \
  ! -path '*/.venv/*' \
  ! -path '*/__pycache__/*' \
  -print0 |
  while IFS= read -r -d '' file; do
    if grep -Iq . "${file}"; then
      perl -0pi -e '
        s/\Q$ENV{TEMPLATE_SNAKE}\E/$ENV{PROJECT_SNAKE}/g;
        s/\Q$ENV{TEMPLATE_SECRET}\E/$ENV{PROJECT_SECRET}/g;
        s/\Q$ENV{TEMPLATE_TITLE}\E/$ENV{PROJECT_TITLE}/g;
        s/\Q$ENV{TEMPLATE_DOCKER_NAME}\E/$ENV{PROJECT_DOCKER_NAME}/g;
      ' "${file}"
    fi
  done

(
  cd "${TARGET_DIR}"
  rm -rf .git
  cp .env.example .env
  git init >/dev/null
)

cat <<EOF
Created ${PROJECT_TITLE} at ${TARGET_DIR}

Next steps:
  cd ${TARGET_DIR}
  python -m venv env
  source env/bin/activate
  pip install -r requirements.txt
  python -m app.cli db:create
  python -m app.cli db:upgrade
  python -m app.cli system:seed
  python -m app.cli spec
EOF
