#!/usr/bin/env bash
set -euo pipefail

docker run --rm \
  --name ministack \
  -p 4566:4566 \
  nahuelnucera/ministack
