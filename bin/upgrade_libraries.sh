#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQUIREMENTS_FILE="${ROOT_DIR}/requirements.txt"

if [[ ! -f "${REQUIREMENTS_FILE}" ]]; then
  printf 'Could not find requirements.txt at %s\n' "${REQUIREMENTS_FILE}" >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-python}"

tmp_file="$(mktemp)"
cleanup() {
  rm -f "${tmp_file}"
}
trap cleanup EXIT

"${PYTHON_BIN}" - "${REQUIREMENTS_FILE}" "${tmp_file}" <<'PY'
import re
import sys
from pathlib import Path

source = Path(sys.argv[1])
target = Path(sys.argv[2])

specifier_pattern = re.compile(r"\s*(===|==|~=|!=|<=|>=|<|>|=)\s*")


def strip_version_specifier(line: str) -> str:
    stripped = line.strip()

    if not stripped or stripped.startswith("#"):
        return line.rstrip("\n")

    if stripped.startswith(("-", "--")):
        return line.rstrip("\n")

    requirement, marker = stripped, ""
    if ";" in stripped:
        requirement, marker = stripped.split(";", 1)
        marker = ";" + marker.strip()

    inline_comment = ""
    if " #" in requirement:
        requirement, inline_comment = requirement.split(" #", 1)
        inline_comment = " #" + inline_comment.strip()

    package_name = specifier_pattern.split(requirement.strip(), maxsplit=1)[0].strip()
    if not package_name:
        return line.rstrip("\n")

    return f"{package_name}{marker}{inline_comment}"


target.write_text(
    "\n".join(strip_version_specifier(line) for line in source.read_text().splitlines()) + "\n"
)
PY

mv "${tmp_file}" "${REQUIREMENTS_FILE}"

"${PYTHON_BIN}" -m pip install --upgrade -r "${REQUIREMENTS_FILE}"
