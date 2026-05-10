#!/usr/bin/env bash

set -euo pipefail

# Allow overriding the MiniStack endpoint to keep this script flexible.
MINISTACK_URL="${MINISTACK_URL:-http://localhost:4566}"

# Allow passing a queue name; default to our report queue with the required FIFO suffix.
QUEUE_NAME="${1:-tphlms.fifo}"

QUEUE_URL="$(aws --endpoint-url="${MINISTACK_URL}" sqs create-queue \
  --queue-name "${QUEUE_NAME}" \
  --attributes FifoQueue=true,ContentBasedDeduplication=true \
  --query 'QueueUrl' \
  --output text)"

printf 'Created development queue: %s\n' "${QUEUE_URL}"
