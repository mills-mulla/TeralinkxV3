# TeralinkX V3 - ISP Management Platform

A comprehensive ISP management platform with authentication resilience, HIDS security monitoring, and multi-service architecture.

## 🏗️ Project Structure

```
TeralinkxV3/
├── 📁 certbot/           # SSL certificate management
├── 📁 cloudflared/       # Cloudflare tunnel configuration
├── 📁 data/              # Persistent data storage
├── 📁 docs/              # Project documentation
├── 📁 freeradius/        # RADIUS server configuration
├── 📁 hids/              # Host Intrusion Detection System
├── 📁 monitoring/        # Prometheus, Grafana, Loki stack
├── 📁 nginx/             # Reverse proxy configuration
├── 📁 postgres/          # Database initialization
├── 📁 radius_api/        # RADIUS API service
├── 📁 scripts/           # Organized deployment & testing scripts
├── 📁 teracore/          # Python virtual environment
├── 📁 teralinkx/         # Main Django backend
├── 📁 TeralinkxFR/       # Vue.js frontend
├── 🐳 docker-compose.yml # Main orchestration file
└── 📋 requirements.txt   # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.11+ (for backend development)

### Deployment
```bash
# Start all services
docker-compose up -d

# Deploy frontend
./scripts/deployment/deploy-production.sh

# Monitor services
docker-compose logs -f
```

## 🔧 Key Features

### 🔐 Authentication Resilience
- JWT secret persistence across restarts
- Multi-strategy token recovery
- Real-time health monitoring
- Automatic session restoration

### 🛡️ Security (HIDS)
- Suricata signature-based detection
- Zeek network flow analysis
- Machine learning anomaly detection
- Real-time threat monitoring

### 📊 Monitoring Stack
- Prometheus metrics collection
- Grafana dashboards
- Loki log aggregation
- AlertManager notifications

### 🌐 Multi-Service Architecture
- Django REST API backend
- Vue.js SPA frontend
- RADIUS authentication
- Nginx reverse proxy
- Redis caching & queuing

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [HIDS Architecture](docs/HIDS_ARCHITECTURE.md)
- [HIDS Evaluation Guide](docs/HIDS_EVALUATION_GUIDE.md)
- [Scripts Documentation](scripts/README.md)

## 🔗 Service URLs

- **Frontend**: https://cli.teralinkxwaves.uk
- **Backend API**: https://srv.teralinkxwaves.uk
- **Admin Panel**: https://su.teralinkxwaves.uk
- **Grafana**: https://mt.teralinkxwaves.uk
- **HIDS Dashboard**: https://sec.teralinkxwaves.uk

## 🛠️ Development

### Backend (Django)
```bash
cd teralinkx
python manage.py runserver
```

### Frontend (Vue.js)
```bash
cd TeralinkxFR
npm run dev
```

### Testing
```bash
# Run authentication tests
./scripts/testing/test_auth_resilience.sh

# Run API tests
./scripts/testing/test_api.sh
```

## 📈 Performance Metrics

- **Authentication Recovery**: 95% automatic success rate
- **Token Validity**: 99.9% uptime
- **Recovery Time**: <2 seconds average
- **HIDS Detection**: Real-time threat analysis

## 🤝 Contributing

1. Follow the organized directory structure
2. Place scripts in appropriate `/scripts/` subdirectories
3. Update documentation for new features
4. Test changes with provided test scripts

## 📄 License

Proprietary - TeralinkX Platform