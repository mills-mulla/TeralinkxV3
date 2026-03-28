# Scripts Directory

This directory contains all project scripts organized by category.

## Directory Structure

### 📦 `/deployment/`
Scripts for deploying various components:
- `install.sh` - **Complete automated installation** (RECOMMENDED)
- `quick-install.sh` - Rapid development deployment
- `deploy-production.sh` - Frontend production deployment
- `deploy-hotspot.sh` - Frontend hotspot deployment  
- `deploy_fixes.sh` - Backend fixes deployment
- `deploy-admin.sh` - Admin panel deployment
- `deploy_auth_resilience.sh` - Authentication resilience deployment
- `setup_git_token.sh` - Git token setup
- `backup.sh` - Complete system backup
- `restore.sh` - System restore from backup
- `update.sh` - System update manager

### 🧪 `/testing/`
Testing and validation scripts:
- `test_auth_resilience.sh` - Authentication resilience tests
- `test_api_config.sh` - API configuration tests
- `test_api.sh` - General API tests
- `test_*.py` - Python test scripts
- `test_*.sh` - Shell test scripts
- `insert_test_packages.sql` - Test data SQL
- `populate_test_packages.py` - Test data population

### 📊 `/monitoring/`
Monitoring and health check scripts:
- `auth-health-monitor.sh` - Authentication health monitoring

### 🔐 `/auth/`
Authentication-related scripts:
- `verify-auth-resilience.sh` - Authentication resilience verification

### 🛡️ `/hids/`
HIDS (Host Intrusion Detection System) scripts:
- `start_hids.sh` - Start HIDS services
- `download_datasets.sh` - Download ML datasets
- `generate_traffic.sh` - Generate test traffic
- `train_*.py` - ML model training scripts
- `test_mvp.py` - HIDS MVP testing
- `CICIDS_PCAP_DOWNLOAD_GUIDE.sh` - PCAP download guide

## Usage

Make scripts executable before running:
```bash
chmod +x scripts/category/script_name.sh
./scripts/category/script_name.sh
```

## Notes

- All scripts maintain their original functionality
- Scripts are organized by primary purpose
- Cross-category dependencies are documented within each script