# Task 5 – Documentation

**Student:** Bishwajeet S  
**Assignment:** CA-II DevOps Case Study (Tasks 1–5)

This document covers architecture, pipeline flow, challenges, and lessons learned. The 5-slide deck is in `presentation/slides.html`.

---

## 1. Architecture

The demo service is a small Flask API (inspired by a typical B.Tech PBL microservice) with Prometheus metrics, packaged as a Docker image and deployed with Kubernetes.

```
Developer  →  GitHub (main / develop)
                 │
                 ▼
         GitHub Actions CI/CD
         Test → Build → Trivy → Deploy
                 │
                 ▼
            Docker Hub
                 │
                 ▼
         Kubernetes cluster
         Deployment (3 replicas, RollingUpdate)
         Service NodePort :30082
         HPA (2–6 pods)
                 │
                 ▼
         Prometheus scrapes /metrics
                 │
                 ▼
         Grafana dashboard
         (uptime, latency, request rate, error rate)
```

**Configuration management:** Ansible playbooks install packages, create `devopsuser`, write config files, harden SSH, and install Docker / Prometheus / Grafana on inventory hosts.

---

## 2. Pipeline flow (Task 1)

Tool: **GitHub Actions** — workflow file `.github/workflows/ci-cd.yml`.  
Diagram: `screenshots/pipeline_diagram.png`.

| Stage | Trigger | What it does |
|--------|---------|----------------|
| Test | push / PR | flake8 + pytest |
| Build | after test | multi-stage Docker build, push tags, Trivy scan |
| Staging | `develop` | `kubectl apply` + rollout status |
| Production | `main` | rolling image update + health check |
| Notify | any failure | prints commit, branch, author |

Production uses Kubernetes **RollingUpdate** (`maxUnavailable: 0`) so pods are replaced without taking the service fully down.

---

## 3. Challenges

| Challenge | What happened | How it was handled |
|-----------|----------------|-------------------|
| Windows + Ansible | Ansible targets Linux hosts | Playbook/inventory written for Ubuntu; run from WSL or a Linux CI runner |
| Windows + Node Exporter | `network_mode: host` / `/proc` mounts fail on Docker Desktop | Node Exporter uses the compose bridge network |
| Non-root container | Gunicorn needs a writable temp directory | `emptyDir` volume at `/tmp`; container UID 1000 matches the Deployment |
| Grafana dashboards empty | Dashboard JSON used `uid: prometheus` but the datasource had no UID | Datasource provisioned with `uid: prometheus` |
| No live Kubernetes API | Local kubeconfig pointed at a stopped cluster | Minikube used to apply YAMLs and show rolling update / rollback |
| Docker Hub / kubeconfig in CI | Secrets are not in this public student repo | Workflow documents required secrets; local evidence is Docker + Minikube |

---

## 4. Lessons learned

1. **Shift-left security** (Capital One / DevSecOps): Trivy in the build job finds image CVEs before deploy, instead of a late security gate.
2. **Idempotent IaC** (Ansible): users, packages, and files stay consistent across hosts; `--check` supports dry-run.
3. **Resilience** (Netflix): multiple replicas + rolling updates + probes avoid a single-process outage like a corrupted monolith DB.
4. **Fast, small teams** (Amazon two-pizza / microservices): a small Flask service can be built, scanned, and rolled independently.
5. **Observability first:** `/metrics` plus Grafana (uptime, latency, error rate) makes incidents visible without guessing.
6. **Rollback is a first-class operation:** `kubectl rollout undo` reverses a bad image without a full rebuild.

These map directly to the case-study answers: Netflix (resilience + chaos-ready architecture), Amazon (independent deploy cadence), Capital One (security in the pipeline).
