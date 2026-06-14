# Bernstein — automated DOKS / Kubernetes deployment
# Single source of truth for the whole lifecycle: provision -> deploy -> init -> verify -> destroy.
#
# Quick start (from this directory):
#   cp .env.example .env && $EDITOR .env   # set DIGITALOCEAN_TOKEN
#   export $(grep -v '^#' .env | xargs)    # or: nix develop (auto-sources .env)
#   make all                               # infra + deploy + init-db
#   make hosts && make smoke               # local DNS + end-to-end check

# Recipes are POSIX sh-compatible on purpose (no /bin/bash hard dependency:
# NixOS and minimal images may not ship it). Make defaults SHELL to /bin/sh.
TF_DIR       := terraform
# Default to your standard kubeconfig (~/.kube/config) — what minikube and a bare
# `kubectl`/`k9s` already use, so local dev "just works" with no env juggling.
# DOKS is the special case: Terraform writes ./kubeconfig, used by `make all`/`infra`.
KUBECONFIG     ?= $(HOME)/.kube/config
export KUBECONFIG
DOKS_KUBECONFIG := $(CURDIR)/kubeconfig

# --- minikube (local, free) -------------------------------------------------
# minikube writes its context to ~/.kube/config (the default), so `make minikube*`,
# `make status/smoke`, bare `kubectl` and `k9s` all see it. 2 nodes mirrors DOKS so
# the base (required anti-affinity, 2 replicas) works unchanged. Override
# MINIKUBE_NODES=1 (then run `make soft-affinity`).
MINIKUBE_NODES      ?= 2

# Manifests grouped by deployment phase (subject order).
MONITORING   := cadvisor.daemonset.yaml
DATA         := postgres.secret.yaml postgres.configmap.yaml postgres.volume.yaml \
                postgres.deployment.yaml postgres.service.yaml \
                redis.configmap.yaml redis.deployment.yaml redis.service.yaml
APP          := poll.deployment.yaml worker.deployment.yaml result.deployment.yaml \
                poll.service.yaml result.service.yaml \
                poll.ingress.yaml result.ingress.yaml
LB           := traefik.ingressclass.yaml traefik.rbac.yaml traefik.deployment.yaml \
                traefik.service.yaml

.DEFAULT_GOAL := help
.PHONY: help all infra kubeconfig deploy init-db hosts smoke status destroy \
        metrics hpa pdb load harden soft-affinity hard-affinity \
        minikube minikube-up minikube-deploy minikube-hosts minikube-smoke minikube-down

help: ## Show this help
	@echo "Bernstein — make targets:"
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

all: infra ## DOKS: provision cluster, deploy stack, init DB
	$(MAKE) deploy  KUBECONFIG=$(DOKS_KUBECONFIG)
	$(MAKE) init-db KUBECONFIG=$(DOKS_KUBECONFIG)

## --- Core (subject) ---------------------------------------------------------

infra: ## Provision the DOKS cluster with Terraform (writes ./kubeconfig)
	cd $(TF_DIR) && terraform init -input=false && terraform apply -auto-approve
	@echo ">> Waiting for nodes to become Ready..."
	KUBECONFIG=$(DOKS_KUBECONFIG) kubectl wait --for=condition=Ready nodes --all --timeout=300s

kubeconfig: ## (Re)generate ./kubeconfig from Terraform state
	cd $(TF_DIR) && terraform apply -auto-approve -target=local_file.kubeconfig

deploy: ## Apply all manifests in subject order
	kubectl apply -f $(MONITORING)
	kubectl apply $(addprefix -f ,$(DATA))
	@echo ">> Waiting for postgres & redis to be ready..."
	kubectl rollout status deploy/postgres --timeout=180s
	kubectl rollout status deploy/redis --timeout=120s
	kubectl apply $(addprefix -f ,$(APP))
	kubectl apply $(addprefix -f ,$(LB))
	kubectl -n kube-public rollout status deploy/traefik --timeout=120s

init-db: ## Create the votes table in PostgreSQL (idempotent)
	@POD=$$(kubectl get pods -l app=postgres -o jsonpath='{.items[0].metadata.name}'); \
	echo ">> Initializing DB on pod $$POD"; \
	echo "CREATE TABLE IF NOT EXISTS votes (id text PRIMARY KEY, vote text NOT NULL);" | \
		kubectl exec -i $$POD -c postgres -- psql -U postgres -d postgres

hosts: ## Append node IPs + poll/result hostnames to /etc/hosts (needs sudo)
	@NODES=$$(kubectl get nodes -o jsonpath='{ $$.items[*].status.addresses[?(@.type=="ExternalIP")].address }'); \
	IP=$$(echo $$NODES | awk '{print $$1}'); \
	echo ">> Mapping $$IP -> poll.dop.io result.dop.io"; \
	echo "$$IP poll.dop.io result.dop.io" | sudo tee -a /etc/hosts

status: ## Show cluster state (pods/services/ingress across namespaces)
	kubectl get pods -o wide
	kubectl get svc,ingress
	kubectl -n kube-public get pods,svc -o wide
	kubectl -n kube-system get ds cadvisor

smoke: ## End-to-end smoke test (vote -> result)
	./scripts/smoke.sh

destroy: ## Tear down the DOKS cluster
	cd $(TF_DIR) && terraform destroy -auto-approve

## --- Production hardening ---------------------------------------------------

metrics: ## Ensure metrics-server is available (managed clusters usually ship it)
	@kubectl top nodes >/dev/null 2>&1 && echo "metrics-server already available" || \
		kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

hpa: metrics ## Apply HorizontalPodAutoscalers for poll & result
	kubectl apply -f poll.hpa.yaml -f result.hpa.yaml
	kubectl get hpa

pdb: ## Apply PodDisruptionBudgets for poll, result, traefik
	kubectl apply -f pdb.yaml
	kubectl get pdb -A

load: ## Generate HTTP load against poll (test autoscaling)
	./scripts/load.sh

soft-affinity: ## Relax anti-affinity required->preferred (for clusters with nodes < replicas)
	./scripts/soft-affinity.sh on

hard-affinity: ## Restore strict anti-affinity (preferred->required)
	./scripts/soft-affinity.sh off

harden: pdb hpa ## Apply HPA + PDB

## --- Local cluster (minikube, no DigitalOcean) ------------------------------

minikube: minikube-up minikube-deploy ## One-shot: local cluster + full stack + DB
	@echo ">> Done. Next: 'make minikube-hosts' then open http://poll.dop.io:30021"

minikube-up: ## Start local minikube (docker driver) + metrics-server + default storage
	minikube start --nodes $(MINIKUBE_NODES) --driver=docker \
		--addons=metrics-server,default-storageclass,storage-provisioner

minikube-deploy: ## Deploy the stack + init DB onto the running minikube
	$(MAKE) deploy
	$(MAKE) init-db

minikube-hosts: ## Map the minikube IP -> poll/result hostnames (/etc/hosts; NixOS-aware)
	@IP=$$(minikube ip); LINE="$$IP poll.dop.io result.dop.io"; \
	echo "$$LINE" | sudo tee -a /etc/hosts 2>/dev/null \
	  || { echo ">> /etc/hosts is read-only (NixOS). Add to configuration.nix then nixos-rebuild switch:"; \
	       echo "     networking.extraHosts = \"$$LINE\";"; \
	       echo ">> Or skip it entirely and verify with: make minikube-smoke"; }

minikube-smoke: ## End-to-end check on minikube without /etc/hosts (curl --resolve)
	RESOLVE_IP=$$(minikube ip) ./scripts/smoke.sh

minikube-down: ## Delete the local minikube cluster
	minikube delete
