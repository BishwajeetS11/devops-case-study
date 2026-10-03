# DevOps Case Study – CA-II Assignment

**Student:** Bishwajeet S  
**Repository:** [BishwajeetS11/devops-case-study](https://github.com/BishwajeetS11/devops-case-study)

---

## 📁 Project Structure

```
devops-case-study/
├── app/                          # Task 3 – Flask Microservice
│   ├── app.py                    # Application with Prometheus metrics
│   ├── requirements.txt
│   └── Dockerfile                # Multi-stage build
│
├── tests/                        # Unit tests used by CI
│   └── test_app.py
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # Task 1 – GitHub Actions Pipeline
│
├── ansible/                      # Task 2 – Configuration Management
│   ├── inventory.ini             # Host inventory
│   ├── ansible.cfg
│   └── playbook.yml              # 3-play Ansible playbook
│
├── k8s/                          # Task 3 – Kubernetes Orchestration
│   ├── deployment.yaml           # Rolling update deployment (3 replicas)
│   ├── service.yaml              # NodePort service + HPA
│   ├── configmap.yaml            # Environment config
│   └── rolling-update.md         # Rolling update & rollback commands
│
├── monitoring/                   # Task 4 – Monitoring Stack
│   ├── docker-compose.yml        # App + Prometheus + Grafana + Node Exporter
│   ├── prometheus.yml            # Scrape config
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/      # Auto-provision Prometheus datasource
│       │   └── dashboards/       # Auto-provision dashboard provider
│       └── dashboards/
│           └── app-dashboard.json  # Custom Grafana dashboard
│
├── screenshots/                  # Evidence (app, pipeline, Grafana, K8s)
├── presentation/
│   └── slides.html               # Task 5 – 5 slides
├── docs/
│   └── DOCUMENTATION.md          # Task 5 – Architecture, pipeline, lessons
│
└── README.md
```

---

## 🚀 Task 1 – Deployment Strategy (GitHub Actions)

**Tool:** GitHub Actions  
**Workflow:** [`.github/workflows/ci-cd.yml`](.github/workflows/ci-cd.yml)  
**Pipeline diagram:** [`screenshots/pipeline_diagram.png`](screenshots/pipeline_diagram.png)

### Pipeline Stages

```
┌─────────┐    ┌─────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  Test   │───▶│  Build  │───▶│ Deploy (Staging) │───▶│ Deploy (Production) │
│  Lint   │    │  Push   │    │   develop branch  │    │    main branch      │
│  Pytest │    │  Docker │    │                  │    │  Rolling Update     │
└─────────┘    └─────────┘    └──────────────────┘    └─────────────────────┘
                    │
                    ▼
             ┌──────────────┐
             │ Trivy Scan   │
             │ (Vuln Check) │
             └──────────────┘
```

### Required GitHub Secrets
| Secret | Description |
|--------|-------------|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub token |
| `KUBECONFIG_STAGING` | Base64-encoded kubeconfig for staging |
| `KUBECONFIG_PROD` | Base64-encoded kubeconfig for production |

---

## ⚙️ Task 2 – Configuration Management (Ansible)

**Tool:** Ansible  
**Files:** `ansible/playbook.yml`, `ansible/inventory.ini`

### Playbook Structure
| Play | Hosts | Purpose |
|------|-------|---------|
| Play 1 | all_servers | System update, user creation, security hardening, firewall |
| Play 2 | webservers | Docker install, app deployment, health verification |
| Play 3 | monitoring | Prometheus + Grafana installation and configuration |

### Run Commands
```bash
# Full run
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml

# Only install packages
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml --tags packages

# Only deploy app
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml --tags deploy

# Dry run (no changes)
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml --check
```

---

## 🐳 Task 3 – Containerization & Orchestration

### Docker Build & Run
```bash
# Build image
docker build -t bishwajeets11/devops-case-study-app:latest ./app

# Run locally
docker run -p 5000:5000 bishwajeets11/devops-case-study-app:latest

# Test endpoints
curl http://localhost:5000/
curl http://localhost:5000/health
curl http://localhost:5000/api/data
curl http://localhost:5000/metrics
```

### Kubernetes Deployment
```bash
# Apply all manifests
kubectl apply -f k8s/

# Check rollout status
kubectl rollout status deployment/devops-case-study-app

# View pods
kubectl get pods -l app=devops-case-study-app
```

### Rolling Update
```bash
# Update image to new version
kubectl set image deployment/devops-case-study-app \
  app=bishwajeets11/devops-case-study-app:v2.0.0

# Watch rolling update progress
kubectl rollout status deployment/devops-case-study-app --timeout=120s

# Watch pods being replaced
kubectl get pods -w -l app=devops-case-study-app
```

### Rollback
```bash
# Rollback to previous version (immediate)
kubectl rollout undo deployment/devops-case-study-app

# Rollback to specific revision
kubectl rollout history deployment/devops-case-study-app
kubectl rollout undo deployment/devops-case-study-app --to-revision=1

# Verify rollback
kubectl rollout status deployment/devops-case-study-app
kubectl describe deployment devops-case-study-app
```

Evidence screenshots: `screenshots/k8s_rollout_status.png`, `screenshots/k8s_rollback.png`

---

## 📊 Task 4 – Monitoring & Logging (Prometheus + Grafana)

---

## 📊 Task 4 – Monitoring & Logging (Prometheus + Grafana)

### Start Monitoring Stack
```bash
cd monitoring/
docker-compose up -d
```

### Access URLs
| Service | URL | Credentials |
|---------|-----|-------------|
| Flask App | http://localhost:5000 | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / devops123 |

### Dashboard Metrics
- **Uptime** — `time() - process_start_time_seconds`
- **Request Rate** — `rate(http_requests_total[1m])` per endpoint
- **Latency** — p50 / p95 / p99 percentiles via histogram
- **Error Rate** — `rate(http_errors_total[5m])`

Screenshots: `screenshots/grafana_dashboard.png`, `screenshots/prometheus_targets.png`

---

## 🏗️ Architecture Overview

```
         ┌───────────────────────────────────────────────────┐
         │                  GitHub Actions CI/CD              │
         │  Push → Test → Build → Security Scan → Deploy     │
         └───────────────────────────┬───────────────────────┘
                                     │
                            ┌────────▼────────┐
                            │   Docker Hub    │
                            │  (Image Store)  │
                            └────────┬────────┘
                                     │
                 ┌───────────────────▼───────────────────┐
                 │         Kubernetes Cluster             │
                 │  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
                 │  │  Pod 1  │ │  Pod 2  │ │  Pod 3  │ │  ◀── HPA (2–6)
                 │  │ Flask   │ │ Flask   │ │ Flask   │ │
                 │  └────┬────┘ └────┬────┘ └────┬────┘ │
                 │       └──────────┬┘            │      │
                 │            ┌─────▼─────┐       │      │
                 │            │  Service  │       │      │
                 │            │ NodePort  │       │      │
                 │            │  :30082   │       │      │
                 └────────────┴───────────┴───────┴──────┘
                                     │
              ┌──────────────────────▼──────────────────────┐
              │              Monitoring Stack                │
              │  Prometheus (9090) ◀── scrape /metrics       │
              │       │                                      │
              │  Grafana (3000) ◀── visualise metrics        │
              │  Node Exporter (9100) ◀── host metrics       │
              └─────────────────────────────────────────────┘
```

---

## 📋 Task 5 – Reflection & Report

- **Slides (4–5):** open [`presentation/slides.html`](presentation/slides.html) in a browser (arrow keys to navigate).
- **Documentation:** [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md) — architecture, pipeline flow, challenges, lessons learned.

| Challenge | Solution |
|-----------|----------|
| Monolithic single-point-of-failure | Microservices + Kubernetes HPA |
| Manual deployments (human error) | GitHub Actions full automation |
| Configuration drift across servers | Ansible idempotent playbooks |
| No visibility into production | Prometheus + Grafana dashboards |
| Long release cycles | CI/CD pipeline reduces release time to minutes |
| Security as afterthought | Trivy image scanning in pipeline (shift-left) |
| Zero-downtime deploys | K8s RollingUpdate (maxUnavailable=0) |

---

## 🏅 Bonus – External DevOps challenge

Not included. Add proof here if you submit a Kaggle / Devpost / Cloud hackathon entry or a public GitHub PR badge.

---

*Assignment submitted as part of CA-II – DevOps Case Study Evaluation*
