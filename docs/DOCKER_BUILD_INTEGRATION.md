# Docker Build Integration Analysis
**TeralinkX V3 - Complete Docker Services Review**

Generated: $(date)

---

## 📦 **All Docker Services in TeralinkxV3**

### **Services Using Custom Dockerfiles (Build)**

| Service | Dockerfile Location | Port | Entrypoint | Status |
|---------|-------------------|------|------------|--------|
| **web** | `teralinkx/Dockerfile` | 8000 | `entrypoint.sh` | ✅ Integrated |
| **celery** | `teralinkx/Dockerfile` | - | `entrypoint.sh` | ✅ Integrated |
| **celery_beat** | `teralinkx/Dockerfile` | - | `entrypoint.sh` | ✅ Integrated |
| **radius_api** | `radius_api/Dockerfile` | 8001 | `entrypoint.sh` | ✅ Integrated |
| **hids_dashboard** | `hids/dashboard/Dockerfile` | 5002 | None | ⚠️ Needs Integration |
| **hids_engine** | `hids/engine/Dockerfile` | 5003 | None | ⚠️ Needs Integration |
| **ml_service** | `hids/ml_service/Dockerfile` | 5001 | None | ⚠️ Needs Integration |
| **tcpreplay** | `hids/tcpreplay/Dockerfile` | - | None | ⚠️ Needs Integration |

### **Services Using Pre-built Images**

| Service | Image | Port | Integrated |
|---------|-------|------|------------|
| **nginx** | `nginx:1.25-alpine` | 80, 443 | ✅ Yes |
| **certbot** | `certbot/dns-cloudflare:latest` | - | ✅ Yes |
| **cloudflared** | `cloudflare/cloudflared:latest` | - | ✅ Yes |
| **redis** | `redis:7-alpine` | 6379 | ✅ Yes |
| **postgres** | `postgres:15` | 5432 | ✅ Yes |
| **freeradius** | `freeradius/freeradius-server:latest` | 1812, 1813 | ✅ Yes |
| **suricata** | `jasonish/suricata:latest` | - | ✅ Yes |
| **zeek** | `zeek/zeek:latest` | - | ✅ Yes |
| **jupyter** | `quay.io/jupyter/scipy-notebook:latest` | 8888 | ✅ Yes |
| **prometheus** | `prom/prometheus:latest` | 9090 | ✅ Yes |
| **grafana** | `grafana/grafana:latest` | 3000 | ✅ Yes |
| **loki** | `grafana/loki:latest` | 3100 | ✅ Yes |
| **promtail** | `grafana/promtail:latest` | - | ✅ Yes |
| **alertmanager** | `prom/alertmanager:latest` | 9093 | ✅ Yes |
| **node-exporter** | `prom/node-exporter:latest` | 9100 | ✅ Yes |
| **cadvisor** | `gcr.io/cadvisor/cadvisor:latest` | 8080 | ✅ Yes |
| **redis-exporter** | `oliver006/redis_exporter:latest` | 9121 | ✅ Yes |
| **postgres-exporter** | `prometheuscommunity/postgres-exporter:latest` | 9187 | ✅ Yes |

---

## ⚠️ **Services NOT Integrated with Install Script**

### **1. HIDS Dashboard** (`hids/dashboard/Dockerfile`)

**Current State:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5002
CMD ["python", "app.py"]
```

**Issues:**
- ❌ No entrypoint script for initialization
- ❌ No database connection validation
- ❌ No environment variable configuration
- ❌ Hardcoded database credentials in app.py
- ❌ No health checks before starting

**Required Environment Variables:**
```bash
POSTGRES_HOST=db
POSTGRES_DB=hids
POSTGRES_USER=hids
POSTGRES_PASSWORD=hidspass
```

---

### **2. HIDS Engine** (`hids/engine/Dockerfile`)

**Current State:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "engine.py"]
```

**Issues:**
- ❌ No entrypoint script
- ❌ No database schema initialization check
- ❌ No wait for dependencies (Redis, PostgreSQL, ML service)
- ❌ Hardcoded service URLs
- ❌ No graceful startup sequence

**Required Environment Variables:**
```bash
REDIS_HOST=redis
POSTGRES_HOST=db
POSTGRES_DB=hids
POSTGRES_USER=hids
POSTGRES_PASSWORD=hidspass
ML_SERVICE_URL=http://hids_ml_service:5001
```

---

### **3. ML Service** (`hids/ml_service/Dockerfile`)

**Current State:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "app.py"]
```

**Issues:**
- ❌ No model validation on startup
- ❌ No database connection for analytics
- ❌ No environment variable configuration
- ❌ Model files not checked before starting
- ❌ No fallback if model missing

**Required Environment Variables:**
```bash
POSTGRES_HOST=db
POSTGRES_DB=hids
POSTGRES_USER=hids
POSTGRES_PASSWORD=hidspass
MODEL_PATH=/app/models/anomaly_detector.pkl
SCALER_PATH=/app/models/scaler.pkl
```

---

### **4. TCPReplay** (`hids/tcpreplay/Dockerfile`)

**Current State:**
```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    build-essential git autoconf automake libtool autogen \
    libpcap-dev tcpdump iproute2 iputils-ping \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp
RUN git clone https://github.com/appneta/tcpreplay.git && \
    cd tcpreplay && ./autogen.sh && ./configure && \
    make && make install && ldconfig && \
    cd / && rm -rf /tmp/tcpreplay
WORKDIR /pcaps
ENTRYPOINT ["tcpreplay"]
CMD ["--version"]
```

**Issues:**
- ❌ No integration with install script
- ❌ No PCAP file validation
- ❌ No network interface configuration
- ❌ Manual usage required

**Required Configuration:**
```bash
PCAP_DIR=/pcaps
NETWORK_INTERFACE=br-c51890515ece
```

---

## 🔧 **Recommended Fixes**

### **Priority 1: HIDS Services Integration**

#### **Create Entrypoint Scripts**

**hids/dashboard/entrypoint.sh:**
```bash
#!/bin/bash
set -e

echo "🚀 Starting HIDS Dashboard..."

# Wait for database
echo "Waiting for database..."
while ! nc -z ${POSTGRES_HOST:-db} ${POSTGRES_PORT:-5432}; do
  sleep 2
done
echo "✅ Database is ready!"

# Wait for HIDS engine
echo "Waiting for HIDS engine..."
while ! nc -z hids_engine 5003; do
  sleep 2
done
echo "✅ HIDS engine is ready!"

echo "🎉 Starting dashboard server..."
exec "$@"
```

**hids/engine/entrypoint.sh:**
```bash
#!/bin/bash
set -e

echo "🚀 Starting HIDS Engine..."

# Wait for database
echo "Waiting for database..."
while ! nc -z ${POSTGRES_HOST:-db} ${POSTGRES_PORT:-5432}; do
  sleep 2
done
echo "✅ Database is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} 6379; do
  sleep 2
done
echo "✅ Redis is ready!"

# Wait for ML service
echo "Waiting for ML service..."
while ! nc -z hids_ml_service 5001; do
  sleep 2
done
echo "✅ ML service is ready!"

# Initialize database schema
echo "📝 Initializing HIDS schema..."
python -c "from engine import init_schema; init_schema()"

echo "🎉 Starting HIDS engine..."
exec "$@"
```

**hids/ml_service/entrypoint.sh:**
```bash
#!/bin/bash
set -e

echo "🚀 Starting ML Service..."

# Check if model exists
if [ ! -f "/app/models/anomaly_detector.pkl" ]; then
  echo "⚠️  No trained model found!"
  echo "Creating default model..."
fi

# Wait for database (for analytics)
echo "Waiting for database..."
while ! nc -z ${POSTGRES_HOST:-db} ${POSTGRES_PORT:-5432}; do
  sleep 2
done
echo "✅ Database is ready!"

echo "🎉 Starting ML service..."
exec "$@"
```

---

### **Priority 2: Update Dockerfiles**

**Add netcat to HIDS Dockerfiles:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install netcat for health checks
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add entrypoint
RUN chmod +x entrypoint.sh

EXPOSE 5002

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "app.py"]
```

---

### **Priority 3: Update Install Script**

**Add HIDS database configuration:**
```bash
# HIDS Database Configuration
read -p "Enter HIDS database name [hids]: " HIDS_DB_NAME
HIDS_DB_NAME=${HIDS_DB_NAME:-hids}

read -p "Enter HIDS database username [hids]: " HIDS_DB_USER
HIDS_DB_USER=${HIDS_DB_USER:-hids}

read -s -p "Enter HIDS database password [hidspass]: " HIDS_DB_PASSWORD
echo
HIDS_DB_PASSWORD=${HIDS_DB_PASSWORD:-hidspass}
```

**Add HIDS environment files:**
```bash
# HIDS Dashboard .env
cat > "$PROJECT_ROOT/hids/dashboard/.env" << EOF
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=$HIDS_DB_NAME
POSTGRES_USER=$HIDS_DB_USER
POSTGRES_PASSWORD=$HIDS_DB_PASSWORD
DASHBOARD_PORT=5002
EOF

# HIDS Engine .env
cat > "$PROJECT_ROOT/hids/engine/.env" << EOF
REDIS_HOST=redis
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=$HIDS_DB_NAME
POSTGRES_USER=$HIDS_DB_USER
POSTGRES_PASSWORD=$HIDS_DB_PASSWORD
ML_SERVICE_URL=http://hids_ml_service:5001
ENGINE_PORT=5003
EOF

# ML Service .env
cat > "$PROJECT_ROOT/hids/ml_service/.env" << EOF
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=$HIDS_DB_NAME
POSTGRES_USER=$HIDS_DB_USER
POSTGRES_PASSWORD=$HIDS_DB_PASSWORD
MODEL_PATH=/app/models/anomaly_detector.pkl
SCALER_PATH=/app/models/scaler.pkl
ML_SERVICE_PORT=5001
EOF
```

---

## 📊 **Integration Status Summary**

### **✅ Fully Integrated (11 services)**
- Django Web App
- Celery Worker
- Celery Beat
- RADIUS API
- Nginx
- PostgreSQL
- Redis
- FreeRADIUS
- Certbot
- Cloudflared
- All monitoring services (Prometheus, Grafana, etc.)

### **⚠️ Needs Integration (4 services)**
- HIDS Dashboard
- HIDS Engine
- ML Service
- TCPReplay

### **🎯 Integration Checklist**

- [ ] Create entrypoint scripts for HIDS services
- [ ] Update HIDS Dockerfiles with netcat
- [ ] Add HIDS database configuration to install script
- [ ] Create HIDS environment files
- [ ] Add HIDS health checks to deployment
- [ ] Update docker-compose.yml with environment variables
- [ ] Test HIDS service startup sequence
- [ ] Document HIDS configuration in installation report

---

## 🚀 **Next Steps**

1. **Create entrypoint scripts** for all HIDS services
2. **Update Dockerfiles** to use entrypoints
3. **Modify install script** to configure HIDS services
4. **Add health checks** for HIDS services in deployment
5. **Test complete installation** with HIDS enabled
6. **Update documentation** with HIDS configuration

---

## 📝 **Notes**

- All Django apps (web, celery, radius_api) are now fully integrated with dynamic configuration
- HIDS services need similar treatment for production readiness
- TCPReplay is a utility service and may not need full integration
- Consider adding HIDS database initialization to postgres init script

