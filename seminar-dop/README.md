<!-- markdownlint-disable MD033 -->
<div align="center">
  <img src="docs/assets/epitech.png" alt="Epitech Logo" width="400" />
  <br />
  <img src="https://img.shields.io/badge/Seminar-Kubernetes_Orchestration-6366f1?style=for-the-badge" alt="Seminar Badge" />
  <img src="https://img.shields.io/badge/Days-121--135-00f2a6?style=for-the-badge" alt="Days Badge" />
  <img src="https://img.shields.io/badge/Focus-Container_Orchestration-ff4757?style=for-the-badge" alt="Focus Badge" />
</div>
<!-- markdownlint-enable MD033 -->

# Seminar: DOP — Bernstein (Kubernetes Orchestration)

Mastering container orchestration at scale: deploying distributed voting applications on Kubernetes clusters, infrastructure-as-code provisioning with Terraform, and cloud-native networking with Traefik.

---

> [!IMPORTANT]
> **Core Objectives**: 
> - **Kubernetes Mastery**: Multi-node cluster deployment and pod orchestration.
> - **Infrastructure as Code**: Cloud provisioning with Terraform on DigitalOcean (DOKS).
> - **Microservices Architecture**: Distributed voting system (Flask, Redis, Java worker, PostgreSQL, Node.js dashboard).
> - **Load Balancing**: Traefik reverse proxy for service routing and high availability.
> - **Reproducible DevOps**: Nix-based development environments for consistency.

## Technical Core

| Layer | Implementation |
|---|---|
| **Orchestration** | ![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white) ![Helm](https://img.shields.io/badge/Helm-0F1689?style=flat-square&logo=helm&logoColor=white) |
| **Infrastructure** | ![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white) ![DigitalOcean](https://img.shields.io/badge/DOKS-0080FF?style=flat-square&logo=digitalocean&logoColor=white) |
| **Networking** | ![Traefik](https://img.shields.io/badge/Traefik-24A1C1?style=flat-square&logo=traefikproxy&logoColor=white) ![Ingress](https://img.shields.io/badge/Ingress-Cloud_Native-336791?style=flat-square) |
| **Services** | ![Flask](https://img.shields.io/badge/Frontend-Flask-000000?style=flat-square&logo=flask&logoColor=white) ![Redis](https://img.shields.io/badge/Queue-Redis-DC382D?style=flat-square&logo=redis&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/DB-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white) |

---

## Chronological Journey

- **Days 121-122**: Bootstrap — Local Minikube essentials (pods, services, ConfigMaps).
- **Days 123-132**: **Bernstein Project** — Full distributed voting app on managed Kubernetes (DOKS).
- **Days 133-135**: **Infrastructure & Automation** — Terraform provisioning, monitoring with cAdvisor, and hardening.

---

## Project Deliverables

See [Day 121-135](Day_121_135/) for:
- **[README.md](Day_121_135/README.md)** — Project details and deployment architecture
- **[OBJECTIVES.md](Day_121_135/OBJECTIVES.md)** — Core learning outcomes
- **[solutions_day121_135/](Day_121_135/solutions_day121_135/)** — All Kubernetes manifests, Terraform code, and bootstrap exercises
