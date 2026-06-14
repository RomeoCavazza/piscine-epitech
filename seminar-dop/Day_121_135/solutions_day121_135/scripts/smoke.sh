#!/usr/bin/env bash
# Bernstein — end-to-end smoke test.
# Proves the public path (Traefik -> poll/result) and dumps cluster state.
#
# Default: relies on /etc/hosts mapping poll.dop.io / result.dop.io to a node IP.
# Without /etc/hosts (e.g. NixOS / minikube), resolve via curl instead:
#   RESOLVE_IP=$(minikube ip) ./scripts/smoke.sh      # or: make minikube-smoke
set -euo pipefail

PORT="${PORT:-30021}"
DASH_PORT="${DASH_PORT:-30042}"
POLL_URL="${POLL_URL:-http://poll.dop.io:$PORT}"
RESULT_URL="${RESULT_URL:-http://result.dop.io:$PORT}"

# When RESOLVE_IP is set, send the right Host header but resolve to the node IP
# (no /etc/hosts needed). Also points the Traefik dashboard at that IP.
RESOLVE=()
if [ -n "${RESOLVE_IP:-}" ]; then
  RESOLVE=(--resolve "poll.dop.io:$PORT:$RESOLVE_IP" --resolve "result.dop.io:$PORT:$RESOLVE_IP")
  TRAEFIK_PING="${TRAEFIK_PING:-http://$RESOLVE_IP:$DASH_PORT/ping}"
else
  TRAEFIK_PING="${TRAEFIK_PING:-http://localhost:$DASH_PORT/ping}"
fi

pass() { printf '  \033[0;32m✓\033[0m %s\n' "$1"; }
fail() { printf '  \033[0;31m✗\033[0m %s\n' "$1"; exit 1; }

echo "== HTTP reachability =="

code=$(curl -fsS "${RESOLVE[@]}" -o /dev/null -w '%{http_code}' "$POLL_URL") \
  && pass "poll  ($POLL_URL) -> HTTP $code" \
  || fail "poll  ($POLL_URL) unreachable"

# The poll page footer prints the serving pod id ("Processed by container ID ...").
served=$(curl -fsS "${RESOLVE[@]}" "$POLL_URL" | grep -io 'container ID[^<]*' | head -n1 || true)
[ -n "$served" ] && pass "served by: $served"

code=$(curl -fsS "${RESOLVE[@]}" -o /dev/null -w '%{http_code}' "$RESULT_URL") \
  && pass "result ($RESULT_URL) -> HTTP $code" \
  || fail "result ($RESULT_URL) unreachable"

code=$(curl -fsS -o /dev/null -w '%{http_code}' "$TRAEFIK_PING") \
  && pass "traefik /ping -> HTTP $code" \
  || echo "  (traefik /ping not reachable from here — ok if not port-forwarded)"

# Best-effort vote POST (option ids depend on the build; non-fatal).
echo "== Cast a test vote (best effort) =="
curl -fsS "${RESOLVE[@]}" -X POST -d 'vote=a' "$POLL_URL" -o /dev/null \
  && pass "POST vote=a accepted" \
  || echo "  (vote POST skipped/failed — check option ids on the poll page)"

echo "== Cluster state =="
kubectl get pods -o wide
kubectl get svc,ingress
kubectl -n kube-public get pods,svc -o wide

echo "== Smoke test OK =="
