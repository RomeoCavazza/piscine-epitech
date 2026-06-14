# Days 121–135 — Kubernetes Orchestration & Distributed Voting

- **Objectives**: [OBJECTIVES.md](OBJECTIVES.md)
- **Project Deliverables**: [solutions_day121_135/](solutions_day121_135/)

## Project Overview

**15 days** (concurrent with AI) of cloud-native orchestration: bootstrap with Minikube, then deploy a production-grade distributed voting system on DigitalOcean Kubernetes (DOKS) with Terraform-provisioned infrastructure, Traefik ingress routing, and comprehensive monitoring.

---

## Architecture

### Event-Driven Microservices Pattern

User casts a vote through a **Flask web interface** → vote pushed to **Redis queue** → **Java worker** consumes queue and persists to **PostgreSQL** → **Node.js dashboard** reads database and displays live results with WebSockets. All external traffic routes through **Traefik** reverse proxy.

| Service | Technology | Role | Replicas | Port |
|---------|:----------:|------|:--------:|:----:|
| **poll** | Python/Flask | Web voting interface | 2 | 80 |
| **redis** | Redis | In-memory vote queue | 1 | 6379 |
| **worker** | Java | Queue consumer & DB writer | 1 | — |
| **postgres** | PostgreSQL | Persistent storage | 1 | 5432 |
| **result** | Node.js/Express | Live results dashboard | 2 | 80 |
| **traefik** | Traefik 2.7 | Reverse proxy & LB | 2 | 80, 8080 |
| **cadvisor** | Google cAdvisor | Resource monitoring | DaemonSet | — |

---

## Deployment Phases

### Phase 1: Bootstrap (Days 121-122)
Local Minikube essentials:
- Basic pod creation and lifecycle
- Service discovery and ClusterIP
- ConfigMap and Secret management

See: [bootstrap/](solutions_day121_135/bootstrap/)

### Phase 2: Bernstein Project (Days 123-132)
Production-grade DOKS cluster:
- Multi-node Kubernetes cluster on DigitalOcean
- Manifest-based microservices deployment
- ConfigMaps for shared configuration
- Secrets for database credentials
- Pod anti-affinity for high availability
- Ingress routing with hostname-based rules
- Traefik as cloud-native reverse proxy

See: [Kubernetes manifests](solutions_day121_135/) (root level)

### Phase 3: Infrastructure & Automation (Days 133-135)
Terraform and monitoring:
- Infrastructure as Code on DigitalOcean
- Cluster provisioning and lifecycle
- Terraform state management
- cAdvisor DaemonSet for cluster monitoring
- Resource limits and requests
- Security best practices

See: [terraform/](solutions_day121_135/terraform/), [flake.nix](solutions_day121_135/flake.nix)

---

## Documentation Structure

### Core Kubernetes Manifests
- [poll.deployment.yaml](solutions_day121_135/poll.deployment.yaml) — Flask voting app deployment
- [redis.deployment.yaml](solutions_day121_135/redis.deployment.yaml) — Redis queue deployment
- [worker.deployment.yaml](solutions_day121_135/worker.deployment.yaml) — Java worker deployment
- [postgres.deployment.yaml](solutions_day121_135/postgres.deployment.yaml) — PostgreSQL deployment
- [result.deployment.yaml](solutions_day121_135/result.deployment.yaml) — Node.js results dashboard
- [traefik.deployment.yaml](solutions_day121_135/traefik.deployment.yaml) — Traefik reverse proxy
- [cadvisor.daemonset.yaml](solutions_day121_135/cadvisor.daemonset.yaml) — Node monitoring

### Configuration
- [poll.ingress.yaml](solutions_day121_135/poll.ingress.yaml) & [result.ingress.yaml](solutions_day121_135/result.ingress.yaml) — HTTP routing rules
- [traefik.ingressclass.yaml](solutions_day121_135/traefik.ingressclass.yaml) — Traefik IngressClass resource
- [postgres.configmap.yaml](solutions_day121_135/postgres.configmap.yaml) & [redis.configmap.yaml](solutions_day121_135/redis.configmap.yaml) — ConfigMap data
- [postgres.secret.yaml](solutions_day121_135/postgres.secret.yaml) — Secret credentials
- [postgres.volume.yaml](solutions_day121_135/postgres.volume.yaml) — PersistentVolumeClaim
- [poll.hpa.yaml](solutions_day121_135/poll.hpa.yaml) & [result.hpa.yaml](solutions_day121_135/result.hpa.yaml) — Autoscaling (HPA)
- [pdb.yaml](solutions_day121_135/pdb.yaml) — Pod Disruption Budget (PDB)

### Bootstrap Exercises
- [bootstrap/hello-world.pod.yaml](solutions_day121_135/bootstrap/hello-world.pod.yaml) — Basic pod creation
- [bootstrap/hello-world.service.yaml](solutions_day121_135/bootstrap/hello-world.service.yaml) — Service discovery
- [bootstrap/hello-world.deployment.yaml](solutions_day121_135/bootstrap/hello-world.deployment.yaml) — Deployment management
- [bootstrap/hello-world.volume.yaml](solutions_day121_135/bootstrap/hello-world.volume.yaml) — Storage concepts

### Infrastructure as Code
- [terraform/main.tf](solutions_day121_135/terraform/main.tf) — DOKS cluster provisioning
- [terraform/providers.tf](solutions_day121_135/terraform/providers.tf) — DigitalOcean provider config
- [terraform/variables.tf](solutions_day121_135/terraform/variables.tf) — Input variables
- [terraform/outputs.tf](solutions_day121_135/terraform/outputs.tf) — Output kubeconfig and cluster info
- [flake.nix](solutions_day121_135/flake.nix) — Reproducible Nix dev environment

### Documentation
- [docs/architecture.png](solutions_day121_135/docs/architecture.png) — System architecture diagram
- [docs/cluster-overview.png](solutions_day121_135/docs/cluster-overview.png) — Cluster topology
- [docs/cluster-resources.png](solutions_day121_135/docs/cluster-resources.png) — Resource allocation visualization
- [docs/insights.png](solutions_day121_135/docs/insights.png) — cAdvisor monitoring dashboard
- [docs/poll.png](solutions_day121_135/docs/poll.png) — Voting interface screenshot
- [docs/traefik.png](solutions_day121_135/docs/traefik.png) — Traefik dashboard screenshot
- [docs/result.png](solutions_day121_135/docs/result.png) — Results dashboard screenshot

---

## Key Lessons

- **Kubernetes Architecture**: Master, worker nodes, etcd, kube-apiserver, scheduler, kubelet
- **Pod Lifecycle**: Init containers, health checks (liveness/readiness probes), termination grace periods
- **Networking**: Service types (ClusterIP, NodePort, LoadBalancer), Ingress, DNS service discovery
- **Storage**: PersistentVolumes, PersistentVolumeClaims, storage classes, volume lifecycle
- **Configuration Management**: ConfigMaps for non-sensitive data, Secrets for credentials
- **Scaling**: ReplicaSets, Deployments, Horizontal Pod Autoscaling (HPA)
- **Observability**: Resource metrics (CPU, memory), monitoring with cAdvisor, logging patterns
- **Security**: RBAC, NetworkPolicies, pod security policies, secrets management
- **Infrastructure as Code**: Terraform for reproducible cluster provisioning
- **Cloud-Native Patterns**: 12-factor app principles, stateless services, graceful shutdown
