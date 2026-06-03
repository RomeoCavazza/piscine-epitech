<div align="center">

# Bernstein

### Containers Symphony Orchestration

*Become the Leonard Bernstein of containers — orchestrate a multi-service voting application on Kubernetes.*

<br />

[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Traefik](https://img.shields.io/badge/Traefik-24A1C1?style=for-the-badge&logo=traefikproxy&logoColor=white)](https://traefik.io/)
[![DigitalOcean](https://img.shields.io/badge/DigitalOcean-0080FF?style=for-the-badge&logo=digitalocean&logoColor=white)](https://www.digitalocean.com/)
[![Nix](https://img.shields.io/badge/Nix-5277C3?style=for-the-badge&logo=nixos&logoColor=white)](https://nixos.org/)

<br /><br />

<img src="docs/architecture.png" alt="Bernstein Architecture" width="700" />

</div>

<br />

---

## About

A Kubernetes deployment of a **distributed voting application** across a multi-node cloud cluster. Users vote through a Flask web interface, votes transit via a Redis queue, a Java worker persists them to PostgreSQL, and a Node.js dashboard displays live results — all orchestrated by Traefik as a reverse proxy and load balancer.

Infrastructure is provisioned on **DigitalOcean** (DOKS) via **Terraform**, and the development environment is fully reproducible with **Nix**.

---

## Project Structure

```
bernstein/
│
├── Kubernetes Manifests (root)
│   ├── cadvisor.daemonset.yaml
│   ├── poll.deployment.yaml
│   ├── poll.ingress.yaml
│   ├── poll.service.yaml
│   ├── postgres.configmap.yaml
│   ├── postgres.deployment.yaml
│   ├── postgres.secret.yaml
│   ├── postgres.service.yaml
│   ├── postgres.volume.yaml
│   ├── redis.configmap.yaml
│   ├── redis.deployment.yaml
│   ├── redis.service.yaml
│   ├── result.deployment.yaml
│   ├── result.ingress.yaml
│   ├── result.service.yaml
│   ├── traefik.deployment.yaml
│   ├── traefik.rbac.yaml
│   ├── traefik.service.yaml
│   └── worker.deployment.yaml
│
├── bootstrap/              Local Minikube exercises
│   ├── hello-world.pod.yaml
│   ├── hello-world.service.yaml
│   ├── hello-world.volume.yaml
│   ├── hello-world.deployment.yaml
│   └── flake.nix
│
├── terraform/              DOKS cluster provisioning
│   ├── main.tf
│   ├── outputs.tf
│   ├── providers.tf
│   └── variables.tf
│
├── docs/
│   ├── architecture.png
│   ├── kickoff.pdf
│   └── project.pdf
│
├── .env                    API tokens (git-ignored)
├── .gitignore
├── flake.nix               Nix dev environment
└── README.md
```

---

## How It Works

The application follows a classic **event-driven microservices** pattern. A user casts a vote through a Python/Flask web interface. Instead of writing directly to the database (which would be slow under heavy load), the vote is pushed into a **Redis queue** — an ultra-fast in-memory store that absorbs traffic spikes. A **Java worker** continuously watches that queue, picks up each vote, and writes it into **PostgreSQL** for durable storage. On the other side, a **Node.js** dashboard reads from PostgreSQL and displays live results. All external traffic enters through **Traefik**, a cloud-native reverse proxy that routes requests based on the hostname (`poll.dop.io` vs `result.dop.io`) and load-balances across replicas. A **cAdvisor** DaemonSet monitors resource usage on every node.

Shared configuration (hosts, ports, database name) lives in Kubernetes **ConfigMaps**, while sensitive credentials are stored in **Secrets**. Replicated services use **pod anti-affinity** to guarantee they run on different nodes for high availability.

| Service | Tech | Image | Replicas | Port | Role |
|---------|:----:|-------|:--------:|:----:|------|
| **Poll** | <img src="https://skillicons.dev/icons?i=python" height="24" /> | `epitechcontent/t-dop-600-poll:k8s` | 2 | 80 | Web voting interface |
| **Redis** | <img src="https://skillicons.dev/icons?i=redis" height="24" /> | `redis:5.0` | 1 | 6379 | In-memory vote queue |
| **Worker** | <img src="https://skillicons.dev/icons?i=java" height="24" /> | `epitechcontent/t-dop-600-worker:k8s` | 1 | — | Queue consumer |
| **PostgreSQL** | <img src="https://skillicons.dev/icons?i=postgres" height="24" /> | `postgres:13` | 1 | 5432 | Persistent storage |
| **Result** | <img src="https://skillicons.dev/icons?i=nodejs" height="24" /> | `epitechcontent/t-dop-600-result:k8s` | 2 | 80 | Live results dashboard |
| **Traefik** | <img src="https://skillicons.dev/icons?i=docker" height="24" /> | `traefik:2.7` | 2 | 80, 8080 | Reverse proxy & LB |
| **cAdvisor** | <img src="https://skillicons.dev/icons?i=prometheus" height="24" /> | `gcr.io/cadvisor/cadvisor:latest` | all | 8080 | Container monitoring |

### File Index

Every manifest and configuration file, with a one-line description. All links are clickable.

#### Kubernetes Manifests

| File | Kind | Description |
|------|------|-------------|
| [cadvisor.daemonset.yaml](cadvisor.daemonset.yaml) | DaemonSet | cAdvisor monitoring agent on every node (`kube-system`) |
| [redis.configmap.yaml](redis.configmap.yaml) | ConfigMap | `REDIS_HOST` shared configuration |
| [redis.deployment.yaml](redis.deployment.yaml) | Deployment | Redis 5.0 in-memory vote queue |
| [redis.service.yaml](redis.service.yaml) | Service | ClusterIP exposing Redis on `6379` |
| [postgres.secret.yaml](postgres.secret.yaml) | Secret | `POSTGRES_USER` / `POSTGRES_PASSWORD` credentials |
| [postgres.configmap.yaml](postgres.configmap.yaml) | ConfigMap | `POSTGRES_HOST` / `PORT` / `DB` shared config |
| [postgres.volume.yaml](postgres.volume.yaml) | PV + PVC | Persistent storage for `/var/lib/postgresql/data` |
| [postgres.deployment.yaml](postgres.deployment.yaml) | Deployment | PostgreSQL 13 durable vote storage |
| [postgres.service.yaml](postgres.service.yaml) | Service | ClusterIP exposing Postgres on `5432` |
| [poll.deployment.yaml](poll.deployment.yaml) | Deployment | Flask voting front-end (2 replicas, anti-affinity) |
| [poll.service.yaml](poll.service.yaml) | Service | ClusterIP exposing Poll on `80` |
| [poll.ingress.yaml](poll.ingress.yaml) | Ingress | Traefik route for `poll.dop.io` |
| [worker.deployment.yaml](worker.deployment.yaml) | Deployment | Java queue consumer (Redis → Postgres) |
| [result.deployment.yaml](result.deployment.yaml) | Deployment | Node.js results dashboard (2 replicas, anti-affinity) |
| [result.service.yaml](result.service.yaml) | Service | ClusterIP exposing Result on `80` |
| [result.ingress.yaml](result.ingress.yaml) | Ingress | Traefik route for `result.dop.io` |
| [traefik.rbac.yaml](traefik.rbac.yaml) | RBAC | ServiceAccount + ClusterRole for the Kubernetes API |
| [traefik.deployment.yaml](traefik.deployment.yaml) | Deployment | Traefik 2.7 reverse proxy / LB (2 replicas, `kube-public`) |
| [traefik.service.yaml](traefik.service.yaml) | Service | NodePort `30021` (proxy) + `30042` (dashboard) |

#### Bootstrap (local Minikube)

| File | Description |
|------|-------------|
| [bootstrap/hello-world.pod.yaml](bootstrap/hello-world.pod.yaml) | Single pod with `PORT=8080` env + exposed port |
| [bootstrap/hello-world.service.yaml](bootstrap/hello-world.service.yaml) | ClusterIP service for internal DNS |
| [bootstrap/hello-world.volume.yaml](bootstrap/hello-world.volume.yaml) | 512Mi PersistentVolume + PVC |
| [bootstrap/hello-world.deployment.yaml](bootstrap/hello-world.deployment.yaml) | Pod converted into a Deployment |

#### Infrastructure & Tooling

| File | Description |
|------|-------------|
| [terraform/main.tf](terraform/main.tf) | DOKS cluster (2 worker nodes) |
| [terraform/providers.tf](terraform/providers.tf) | DigitalOcean + local providers |
| [terraform/variables.tf](terraform/variables.tf) | Region & cluster name variables |
| [terraform/outputs.tf](terraform/outputs.tf) | Kubeconfig output + local file generation |
| [flake.nix](flake.nix) | Nix dev shell (kubectl, terraform, doctl…) |

---

## Installation & Configuration

### Prerequisites

- [Nix](https://nixos.org/download.html) package manager
- A [DigitalOcean](https://www.digitalocean.com/) account with an API token
- [Git](https://git-scm.com/)

### Step 1 — Clone & enter environment

```bash
git clone <repo-url> && cd bernstein
cp .env.example .env   # Add your DigitalOcean API token
nix develop            # Loads kubectl, terraform, k9s, helm
```

### Step 2 — Provision cloud cluster

```bash
cd terraform
terraform init
terraform apply        # Creates a 2-worker DOKS cluster (~5 min)
cd ..
export KUBECONFIG=$(pwd)/kubeconfig
```

### Step 3 — Deploy the stack

```bash
# Monitoring
kubectl apply -f cadvisor.daemonset.yaml

# Data layer
kubectl apply -f postgres.secret.yaml \
               -f postgres.configmap.yaml \
               -f postgres.volume.yaml \
               -f postgres.deployment.yaml \
               -f postgres.service.yaml

kubectl apply -f redis.configmap.yaml \
               -f redis.deployment.yaml \
               -f redis.service.yaml

# Application layer
kubectl apply -f poll.deployment.yaml \
               -f worker.deployment.yaml \
               -f result.deployment.yaml \
               -f poll.service.yaml \
               -f result.service.yaml \
               -f poll.ingress.yaml \
               -f result.ingress.yaml

# Load balancer
kubectl apply -f traefik.rbac.yaml \
               -f traefik.deployment.yaml \
               -f traefik.service.yaml
```

### Step 4 — Initialize the database

```bash
POSTGRES_POD=$(kubectl get pods -l app=postgres -o jsonpath='{.items[0].metadata.name}')
echo "CREATE TABLE votes (id text PRIMARY KEY, vote text NOT NULL);" | \
  kubectl exec -i $POSTGRES_POD -c postgres -- psql -U postgres -d postgres
```

### Step 5 — Configure local DNS

```bash
NODES=$(kubectl get nodes -o jsonpath='{ $.items[*].status.addresses[?(@.type=="ExternalIP")].address }')
echo "$NODES poll.dop.io result.dop.io" | sudo tee -a /etc/hosts
```

### Step 6 — Access the application

| Endpoint | URL |
|----------|-----|
| Vote | `http://poll.dop.io:30021` |
| Results | `http://result.dop.io:30021` |
| Traefik Dashboard | `http://localhost:30042` |

### Teardown

```bash
cd terraform && terraform destroy
```

---

<div align="center">

*Epitech Seminar DOP — T-DOP-600*

</div>
