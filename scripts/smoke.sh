#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-18080}"
HOST=127.0.0.1 PORT="$PORT" node apps/api/src/server.mjs >/tmp/sentinelflow-smoke.log 2>&1 &
pid=$!
trap 'kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true' EXIT
for _ in $(seq 1 40); do
  if curl -fs "http://127.0.0.1:${PORT}/healthz" >/dev/null; then
    break
  fi
  sleep .2
done
curl --fail --silent --show-error "http://127.0.0.1:${PORT}/healthz" | grep -q '"status":"ok"'
curl --fail --silent --show-error "http://127.0.0.1:${PORT}/readyz" | grep -q '"ready":true'
curl --fail --silent --show-error "http://127.0.0.1:${PORT}/api/v1/info" | grep -q 'sentinelflow-demo-api'
echo 'Smoke tests passed.'
