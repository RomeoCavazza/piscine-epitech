# Days 121–135 — Objectives & Learning Outcomes

## Core Objectives

- **Kubernetes Fundamentals**: Understand pods, services, deployments, and cluster architecture
- **Multi-Node Orchestration**: Deploy applications across multiple nodes with high availability
- **Infrastructure Automation**: Provision and manage clusters with Terraform
- **Cloud-Native Patterns**: Implement stateless, scalable microservices architectures
- **Monitoring & Observability**: Deploy monitoring stacks (cAdvisor) and understand resource usage
- **Production Hardening**: Security, scaling, health checks, and disaster recovery

## Key Concepts

### Kubernetes Core
- Master components: API server, etcd, scheduler, controller manager
- Worker components: kubelet, container runtime, kube-proxy
- Pods: smallest deployable units, containers, shared networking
- Controllers: Deployments, StatefulSets, DaemonSets, Jobs

### Services & Networking
- Service discovery: DNS, ClusterIP, NodePort, LoadBalancer
- Ingress: HTTP routing, SSL termination, hostname-based routing
- Network policies: pod-to-pod communication control

### Storage & Configuration
- PersistentVolumes and PersistentVolumeClaims
- Storage classes and dynamic provisioning
- ConfigMaps: non-sensitive configuration
- Secrets: sensitive credentials and tokens

### Scaling & Reliability
- Horizontal Pod Autoscaling (HPA) based on metrics
- Resource requests and limits
- Liveness and readiness probes
- Pod disruption budgets

### Infrastructure as Code
- Terraform for cloud provisioning
- DigitalOcean Kubernetes Service (DOKS)
- State management and outputs

## Learning Outcomes

By completion, students will:
1. **Deploy** containerized applications to Kubernetes clusters
2. **Configure** services, networking, and ingress routing
3. **Manage** storage, ConfigMaps, and Secrets
4. **Scale** applications horizontally and automatically
5. **Monitor** resource usage with observability tools
6. **Provision** infrastructure with Terraform
7. **Design** production-ready, fault-tolerant architectures
