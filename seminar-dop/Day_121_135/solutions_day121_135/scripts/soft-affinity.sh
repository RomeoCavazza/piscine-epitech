#!/usr/bin/env sh
# Toggle pod anti-affinity between hard (required, the base default) and soft
# (preferred) on poll/result/traefik — WITHOUT editing the base manifests.
#
# Why: the base uses *required* anti-affinity (true HA: one replica per node).
# That needs a node pool with headroom (nodes > replicas). On a small or local
# cluster (<=2 nodes, minikube), required would leave surplus pods Pending and
# block rolling-update surge / HPA scale-up. Run this to relax just for a demo.
#
# Usage:
#   ./soft-affinity.sh on    # required -> preferred (run on small/local clusters)
#   ./soft-affinity.sh off   # preferred -> required (restore base behaviour)
set -eu

MODE="${1:-}"
[ "$MODE" = "on" ] || [ "$MODE" = "off" ] || {
  echo "usage: $0 on|off" >&2; exit 2; }

# app:namespace triples
TARGETS="poll:default result:default traefik:kube-public"

patch_for() {
  app="$1"
  if [ "$MODE" = "on" ]; then
    cat <<EOF
{"spec":{"template":{"spec":{"affinity":{"podAntiAffinity":{
  "requiredDuringSchedulingIgnoredDuringExecution":null,
  "preferredDuringSchedulingIgnoredDuringExecution":[{"weight":100,"podAffinityTerm":{
    "labelSelector":{"matchExpressions":[{"key":"app","operator":"In","values":["$app"]}]},
    "topologyKey":"kubernetes.io/hostname"}}]}}}}}}
EOF
  else
    cat <<EOF
{"spec":{"template":{"spec":{"affinity":{"podAntiAffinity":{
  "preferredDuringSchedulingIgnoredDuringExecution":null,
  "requiredDuringSchedulingIgnoredDuringExecution":[{
    "labelSelector":{"matchExpressions":[{"key":"app","operator":"In","values":["$app"]}]},
    "topologyKey":"kubernetes.io/hostname"}]}}}}}}
EOF
  fi
}

for t in $TARGETS; do
  app="${t%%:*}"; ns="${t##*:}"
  echo ">> $MODE anti-affinity: deploy/$app (ns $ns)"
  kubectl -n "$ns" patch deployment "$app" --type merge --patch "$(patch_for "$app")"
done

echo ">> done. Check: kubectl get pods -o wide"
