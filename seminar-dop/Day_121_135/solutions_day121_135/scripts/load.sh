#!/usr/bin/env bash
# Bernstein — load generator to trigger HPA autoscaling (B4).
# Watch the effect in another terminal:
#   watch -n2 kubectl get hpa,deploy poll
#   kubectl get pods -l app=poll -o wide -w
#
# Usage:
#   ./scripts/load.sh                 # 60s, auto-detect hey/ab, else curl loop
#   DURATION=120 CONCURRENCY=100 ./scripts/load.sh
set -euo pipefail

POLL_URL="${POLL_URL:-http://poll.dop.io:30021}"
DURATION="${DURATION:-60}"
CONCURRENCY="${CONCURRENCY:-50}"

echo ">> Target:      $POLL_URL"
echo ">> Duration:    ${DURATION}s"
echo ">> Concurrency: $CONCURRENCY"

if command -v hey >/dev/null 2>&1; then
  echo ">> Using hey"
  hey -z "${DURATION}s" -c "$CONCURRENCY" "$POLL_URL"
elif command -v ab >/dev/null 2>&1; then
  echo ">> Using ApacheBench (ab) — ~$((CONCURRENCY * DURATION * 10)) requests"
  ab -t "$DURATION" -c "$CONCURRENCY" "$POLL_URL/"
else
  echo ">> No hey/ab found — falling back to parallel curl loop"
  end=$(( $(date +%s) + DURATION ))
  for _ in $(seq 1 "$CONCURRENCY"); do
    ( while [ "$(date +%s)" -lt "$end" ]; do curl -fsS "$POLL_URL" -o /dev/null || true; done ) &
  done
  wait
fi

echo ">> Load finished. Check: kubectl get hpa"
