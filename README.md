# TeralinkX V3 — ISP Management Platform

> Proprietary software — source visible for evaluation purposes only.  
> © 2024 Mills Mulla. All rights reserved. See [LICENSE](LICENSE).

A production-grade ISP billing and network management platform serving **500+ active subscribers**.  
Built and maintained solo by a single developer. Features RADIUS authentication, ML-powered intrusion  
detection, and a full observability stack — all containerised and self-hosted.

🌐 **Live Platform:**

| Service | URL |
|---|---|
| Frontend | https://cli.teralinkxwaves.uk |
| Backend API | https://srv.teralinkxwaves.uk |
| Admin Panel | https://su.teralinkxwaves.uk |
| Grafana Monitoring | https://mt.teralinkxwaves.uk |
| HIDS Security Dashboard | https://sec.teralinkxwaves.uk |

---

## 🧱 Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Django, FastAPI, Gunicorn, Celery, Celery Beat |
| Frontend | Vue.js 3, Vite |
| Database | PostgreSQL (TimescaleDB), SQLite, Redis |
| Auth | FreeRADIUS, JWT |
| DevOps | Docker, Nginx, Linux, Cloudflare Tunnels, Certbot |
| Monitoring | Prometheus, Grafana, Loki, Promtail, Alertmanager, cAdvisor, Node Exporter |
| Security | Suricata (IDS), Zeek (flow analysis), Scikit-learn (ML anomaly detection) |

---

## ✨ Key Features

### 💳 ISP Billing & Subscriber Management
- Full subscriber lifecycle management — onboarding, billing, suspension, renewal
- RADIUS-based authentication via FreeRADIUS for network access control
- Multi-tenant admin dashboard with role-based access control
- Automated invoicing and payment tracking

### 🛡️ HIDS — Host Intrusion Detection System
- **Suricata** — signature-based threat detection with custom rule sets
- **Zeek** — deep network flow analysis and protocol logging
- **ML pipeline** — scikit-learn anomaly detection model trained on real network traffic
- Real-time threat dashboard at [sec.teralinkxwaves.uk](https://sec.teralinkxwaves.uk)
- ⚠️ Phase 3 (in progress): Active **IPS** (Intrusion Prevention System) for automated threat response

### 📊 Observability Stack
- Prometheus scrapes metrics from all services (Django, Redis, PostgreSQL, containers)
- Grafana dashboards for per-service performance visibility
- Loki + Promtail for centralised log aggregation across all containers
- Alertmanager for automated incident notifications

### 🔐 Authentication Resilience
- JWT secret persistence across container restarts
- Multi-strategy token recovery with <2 second average recovery time
- 99.9% token validity uptime, 95% automatic session restoration rate

### 🌐 Infrastructure
- Fully containerised with Docker Compose — 15+ services orchestrated
- Nginx reverse proxy with SSL termination (Certbot + Cloudflare DNS auto-renewal)
- Secure remote access via Cloudflare Tunnels — no exposed public ports
- Self-hosted on a managed Linux server in Nairobi, Kenya

---

## 🏗️ Project Structure

```
TeralinkxV3/
├── 📁 certbot/           # SSL certificate management (Cloudflare DNS)
├── 📁 cloudflared/       # Cloudflare tunnel configuration
├── 📁 freeradius/        # RADIUS server config & schema
├── 📁 hids/              # HIDS stack (Suricata, Zeek, ML service, dashboard)
│   ├── suricata/         # Rules & config
│   ├── zeek/             # Scripts & logs
│   ├── ml_service/       # Flask + scikit-learn anomaly detection API
│   ├── engine/           # Python log parser & event correlator
│   └── dashboard/        # Flask HIDS dashboard
├── 📁 monitoring/        # Prometheus, Grafana, Loki, Promtail, Alertmanager
├── 📁 nginx/             # Reverse proxy config
├── 📁 postgres/          # DB init scripts (multi-database setup)
├── 📁 radius_api/        # RADIUS management API (FastAPI)
├── 📁 teralinkx/         # Main Django backend
├── 📁 TeralinkxFR/       # Vue.js 3 frontend
├── 📁 scripts/           # Deployment, testing & maintenance scripts
├── 📁 docs/              # Architecture & deployment documentation
└── 🐳 docker-compose.yml # Full stack orchestration (15+ services)
```

---

## 🚀 Deployment

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.11+
- Cloudflare account (for DNS + Tunnels)

### Start the stack
```bash
# Clone and configure environment
cp .env.example .env  # fill in your values

# Start all services
docker-compose up -d

# Deploy frontend
./scripts/deployment/deploy-production.sh

# Monitor
docker-compose logs -f
```

---

## 🛠️ Local Development

```bash
# Backend
cd teralinkx
python manage.py runserver

# Frontend
cd TeralinkxFR
npm run dev

# Run tests
./scripts/testing/test_auth_resilience.sh
./scripts/testing/test_api.sh
```

---

## 📚 Documentation
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [HIDS Architecture](docs/HIDS_ARCHITECTURE.md)
- [HIDS Evaluation Guide](docs/HIDS_EVALUATION_GUIDE.md)
- [Scripts Reference](scripts/README.md)

---

## 📄 License

Copyright © 2024 Mills Mulla. All rights reserved.

This source code is made publicly visible for portfolio and evaluation purposes only.  
Copying, modification, distribution, or use of this code in any form is strictly  
prohibited without explicit written permission from the author.

Contact: sammymulla42@gmail.com
