#!/usr/bin/env bash
set -euo pipefail

MINISTACK_NAME="${MINISTACK_NAME:-ministack}"
AWS_ENDPOINT="${AWS_ENDPOINT:-http://localhost:4566}"
QUEUE_NAME="${QUEUE_NAME:-tphlms.fifo}"

cleanup() {
  docker rm -f "${MINISTACK_NAME}" >/dev/null 2>&1 || true
}

trap cleanup EXIT

cleanup

docker run -d \
  --rm \
  --name "${MINISTACK_NAME}" \
  -p 4566:4566 \
  nahuelnucera/ministack >/dev/null

printf 'Starting MiniStack container "%s" on %s\n' "${MINISTACK_NAME}" "${AWS_ENDPOINT}"

for _ in $(seq 1 30); do
  if aws --endpoint-url="${AWS_ENDPOINT}" sqs list-queues >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if ! aws --endpoint-url="${AWS_ENDPOINT}" sqs list-queues >/dev/null 2>&1; then
  printf 'MiniStack did not become ready in time.\n' >&2
  exit 1
fi

SQS_QUEUE_URL="$(aws --endpoint-url="${AWS_ENDPOINT}" sqs create-queue \
  --queue-name "${QUEUE_NAME}" \
  --attributes FifoQueue=true,ContentBasedDeduplication=true \
  --query 'QueueUrl' \
  --output text)"

cat <<EOF

MiniStack is ready.
Configure your app with:
  export AWS_ENDPOINT=${AWS_ENDPOINT}
  export SQS_QUEUE_URL=${SQS_QUEUE_URL}

EOF

docker logs -f "${MINISTACK_NAME}"
