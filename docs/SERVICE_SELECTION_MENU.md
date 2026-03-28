# Interactive Service Selection Menu - Documentation

**Feature:** Interactive CLI Menu for Service Selection  
**Date:** $(date)  
**Status:** ✅ Implemented

---

## 🎯 **Overview**

The TeralinkX V3 installer now features an interactive service selection menu that allows users to choose exactly which services to install based on their needs.

---

## 📋 **Installation Profiles**

### **1. 🚀 Full Installation (Recommended)**
**Best for:** Production deployments, complete ISP management

**Includes:**
- ✅ Core Services (PostgreSQL, Redis, Celery)
- ✅ Django Web Application
- ✅ RADIUS API + FreeRADIUS
- ✅ Nginx + Certbot + Cloudflared
- ✅ HIDS (Suricata, Zeek, ML Service, Engine, Dashboard)
- ✅ Monitoring (Prometheus, Grafana, Loki, AlertManager, Exporters)
- ✅ Frontend (Vue.js)

**Resources:**
- RAM: ~8GB minimum
- Disk: ~15GB minimum
- Services: ~20 containers

---

### **2. 💼 Enterprise ISP**
**Best for:** Large ISP operations, high availability

**Includes:**
- ✅ Core Services
- ✅ Django Web Application
- ✅ RADIUS API + FreeRADIUS
- ✅ Nginx + Certbot + Cloudflared
- ❌ HIDS (Optional - can add later)
- ✅ Monitoring Stack
- ✅ Frontend

**Resources:**
- RAM: ~6GB minimum
- Disk: ~10GB minimum
- Services: ~15 containers

---

### **3. 🏢 Small Business ISP**
**Best for:** Small to medium ISPs, cost-effective setup

**Includes:**
- ✅ Core Services
- ✅ Django Web Application
- ✅ RADIUS API + FreeRADIUS
- ✅ Nginx + Certbot
- ❌ Cloudflared
- ❌ HIDS
- ❌ Monitoring
- ✅ Frontend

**Resources:**
- RAM: ~4GB minimum
- Disk: ~8GB minimum
- Services: ~10 containers

---

### **4. 🧪 Development/Testing**
**Best for:** Developers, testing environments

**Includes:**
- ✅ Core Services
- ✅ Django Web Application
- ❌ RADIUS API
- ❌ FreeRADIUS
- ✅ Nginx (no SSL)
- ❌ HIDS
- ❌ Monitoring
- ✅ Frontend

**Resources:**
- RAM: ~3GB minimum
- Disk: ~5GB minimum
- Services: ~6 containers

---

### **5. 🎯 Custom Selection**
**Best for:** Advanced users, specific requirements

**Allows selection of:**
- Individual Django applications
- RADIUS components
- SSL/Proxy options
- HIDS components (Suricata, Zeek, ML)
- Monitoring components (Prometheus, Grafana, Loki)
- Frontend build

---

## 🖥️ **Menu Flow**

### **Step 1: Profile Selection**
```
╔══════════════════════════════════════════════════════════════╗
║           TeralinkX V3 - Service Selection Menu             ║
║                  ISP Management Platform                     ║
╚══════════════════════════════════════════════════════════════╝

Select Installation Profile:

1. 🚀 Full Installation (Recommended)
   └─ All services including HIDS and Monitoring

2. 💼 Enterprise ISP
   └─ Core + RADIUS + Monitoring (No HIDS)

3. 🏢 Small Business ISP
   └─ Core + RADIUS only

4. 🧪 Development/Testing
   └─ Core services only (minimal)

5. 🎯 Custom Selection
   └─ Choose individual services

Enter choice (1-5):
```

### **Step 2: Custom Selection (if chosen)**
```
═══════════════════════════════════════════════════════
Select services to install (y/n for each):
═══════════════════════════════════════════════════════

📦 CORE SERVICES (Required):
  ✓ PostgreSQL Database
  ✓ Redis Cache
  ✓ Celery Task Queue

🐍 DJANGO APPLICATIONS:
  ✓ Main Web Application (Required)
  Install RADIUS API? (y/n) [y]:

📡 RADIUS SERVER:
  Install FreeRADIUS? (y/n) [y]:

🌐 REVERSE PROXY & SSL:
  ✓ Nginx (Required)
  Install Certbot (SSL certificates)? (y/n) [y]:
  Install Cloudflared (Cloudflare tunnel)? (y/n) [n]:

🛡️  HIDS - HOST INTRUSION DETECTION (Recommended):
  Install HIDS services? (y/n) [y]:
    Install Suricata IDS? (y/n) [y]:
    Install Zeek Network Monitor? (y/n) [y]:
    Install ML Anomaly Detection? (y/n) [y]:

📊 MONITORING STACK (Recommended):
  Install Monitoring services? (y/n) [y]:
    Install Prometheus? (y/n) [y]:
    Install Grafana? (y/n) [y]:
    Install Loki (Log aggregation)? (y/n) [y]:

🎨 FRONTEND:
  Build and install frontend? (y/n) [y]:
```

### **Step 3: Summary & Confirmation**
```
╔══════════════════════════════════════════════════════════════╗
║              Selected Services Summary                       ║
╚══════════════════════════════════════════════════════════════╝

✓ CORE SERVICES:
  • PostgreSQL Database
  • Redis Cache
  • Celery Task Queue

✓ DJANGO APPLICATIONS:
  • Main Web Application
  • RADIUS API

✓ RADIUS SERVER:
  • FreeRADIUS

✓ REVERSE PROXY & SSL:
  • Nginx
  • Certbot (SSL)
  ✗ Cloudflared

✓ HIDS (Host Intrusion Detection):
  • Suricata IDS
  • Zeek Network Monitor
  • ML Anomaly Detection
  • HIDS Engine
  • HIDS Dashboard

✓ MONITORING STACK:
  • Prometheus
  • Grafana
  • Loki + Promtail
  • AlertManager
  • Exporters (Node, Redis, PostgreSQL)

✓ FRONTEND:
  • Vue.js Application

📊 ESTIMATED RESOURCE REQUIREMENTS:
  • Minimum RAM: 8GB
  • Minimum Disk: 15GB
  • Services to deploy: ~20
  • Estimated deployment time: 5-15 minutes

═══════════════════════════════════════════════════════
Proceed with this configuration? (y/n) [y]:
```

---

## 🔧 **Technical Implementation**

### **Service Variables:**
```bash
# Core (Always installed)
INSTALL_CORE=true
INSTALL_DATABASE=true
INSTALL_REDIS=true
INSTALL_CELERY=true

# Django Apps
INSTALL_WEB=true
INSTALL_RADIUS_API=true/false

# RADIUS
INSTALL_FREERADIUS=true/false

# Proxy & SSL
INSTALL_NGINX=true
INSTALL_CERTBOT=true/false
INSTALL_CLOUDFLARED=true/false

# HIDS
INSTALL_HIDS=true/false
INSTALL_SURICATA=true/false
INSTALL_ZEEK=true/false
INSTALL_ML_SERVICE=true/false

# Monitoring
INSTALL_MONITORING=true/false
INSTALL_PROMETHEUS=true/false
INSTALL_GRAFANA=true/false
INSTALL_LOKI=true/false

# Frontend
INSTALL_FRONTEND=true/false
```

### **Integration with install.sh:**
```bash
# Source service selection menu
source "$SCRIPT_DIR/service_selection.sh"

# Show menu before configuration
show_service_selection_menu

# Variables are exported and used throughout installation
if [[ $INSTALL_HIDS == true ]]; then
    # Deploy HIDS services
fi
```

---

## 📊 **Service Comparison Matrix**

| Service | Full | Enterprise | Small Biz | Dev | Custom |
|---------|------|------------|-----------|-----|--------|
| **Core Services** | ✅ | ✅ | ✅ | ✅ | ✅ |
| PostgreSQL | ✅ | ✅ | ✅ | ✅ | ✅ |
| Redis | ✅ | ✅ | ✅ | ✅ | ✅ |
| Celery | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Django Apps** | | | | | |
| Web App | ✅ | ✅ | ✅ | ✅ | ✅ |
| RADIUS API | ✅ | ✅ | ✅ | ❌ | ⚙️ |
| **RADIUS Server** | | | | | |
| FreeRADIUS | ✅ | ✅ | ✅ | ❌ | ⚙️ |
| **Proxy & SSL** | | | | | |
| Nginx | ✅ | ✅ | ✅ | ✅ | ✅ |
| Certbot | ✅ | ✅ | ✅ | ❌ | ⚙️ |
| Cloudflared | ✅ | ✅ | ❌ | ❌ | ⚙️ |
| **HIDS** | | | | | |
| Suricata | ✅ | ❌ | ❌ | ❌ | ⚙️ |
| Zeek | ✅ | ❌ | ❌ | ❌ | ⚙️ |
| ML Service | ✅ | ❌ | ❌ | ❌ | ⚙️ |
| HIDS Engine | ✅ | ❌ | ❌ | ❌ | ⚙️ |
| HIDS Dashboard | ✅ | ❌ | ❌ | ❌ | ⚙️ |
| **Monitoring** | | | | | |
| Prometheus | ✅ | ✅ | ❌ | ❌ | ⚙️ |
| Grafana | ✅ | ✅ | ❌ | ❌ | ⚙️ |
| Loki | ✅ | ✅ | ❌ | ❌ | ⚙️ |
| AlertManager | ✅ | ✅ | ❌ | ❌ | ⚙️ |
| Exporters | ✅ | ✅ | ❌ | ❌ | ⚙️ |
| **Frontend** | | | | | |
| Vue.js App | ✅ | ✅ | ✅ | ✅ | ⚙️ |

**Legend:**
- ✅ Included
- ❌ Not included
- ⚙️ User choice

---

## 🎯 **Use Cases**

### **Full Installation:**
```bash
./scripts/deployment/install.sh
# Select: 1 (Full Installation)
# Use for: Production ISP with security monitoring
```

### **Enterprise ISP:**
```bash
./scripts/deployment/install.sh
# Select: 2 (Enterprise ISP)
# Use for: Large ISP without HIDS (add later if needed)
```

### **Small Business:**
```bash
./scripts/deployment/install.sh
# Select: 3 (Small Business ISP)
# Use for: Cost-effective ISP setup
```

### **Development:**
```bash
./scripts/deployment/install.sh
# Select: 4 (Development/Testing)
# Use for: Local development, testing features
```

### **Custom:**
```bash
./scripts/deployment/install.sh
# Select: 5 (Custom Selection)
# Use for: Specific requirements, gradual deployment
```

---

## 💡 **Benefits**

### **For Users:**
- ✅ Clear understanding of what will be installed
- ✅ Control over resource usage
- ✅ Ability to start small and scale up
- ✅ Reduced installation time for minimal setups
- ✅ Cost optimization (fewer resources needed)

### **For Administrators:**
- ✅ Flexible deployment options
- ✅ Easy to add services later
- ✅ Better resource planning
- ✅ Simplified troubleshooting
- ✅ Modular architecture

---

## 🔄 **Adding Services Later**

Services can be added after initial installation:

```bash
# Enable HIDS later
docker-compose up -d ml_service hids_engine hids_dashboard suricata zeek

# Enable Monitoring later
docker-compose up -d prometheus grafana loki promtail alertmanager

# Add RADIUS later
docker-compose up -d radius_api freeradius
```

---

## 📝 **Notes**

- Core services (PostgreSQL, Redis, Celery, Nginx, Web App) are always installed
- HIDS is marked as "Recommended" for security
- Monitoring is marked as "Recommended" for operations
- Custom selection allows granular control
- All profiles can be modified after installation

---

**Status:** ✅ **FEATURE COMPLETE AND READY FOR USE**

