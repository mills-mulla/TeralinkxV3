# Deployment Scripts Analysis & Integration Status

**Date:** $(date)
**Project:** TeralinkX V3

---

## 📋 **All Deployment Scripts**

### **1. install.sh** ✅ **FULLY UPDATED**
**Purpose:** Complete system installation with full configuration
**Status:** ✅ Fully integrated with HIDS services
**Features:**
- Interactive configuration collection
- Dynamic environment file generation
- Systematic service deployment
- Comprehensive health checks
- HIDS integration complete
- Detailed installation report

**Recent Updates:**
- ✅ HIDS database configuration
- ✅ HIDS environment files
- ✅ HIDS health checks
- ✅ Systematic HIDS deployment
- ✅ Enhanced reporting

---

### **2. quick-install.sh** ⚠️ **NEEDS UPDATES**
**Purpose:** Rapid deployment with minimal configuration
**Status:** ⚠️ Missing HIDS integration
**Current Issues:**
- ❌ No HIDS configuration
- ❌ Hardcoded credentials (admin/admin123)
- ❌ No HIDS database setup
- ❌ Missing dynamic configuration
- ❌ No health checks

**Required Updates:**
1. Add HIDS quick setup option
2. Generate secure random passwords
3. Add HIDS database initialization
4. Include basic health checks
5. Update to use dynamic ports

---

### **3. backup.sh** ⚠️ **NEEDS HIDS INTEGRATION**
**Purpose:** Create comprehensive system backups
**Status:** ⚠️ Partially complete - missing HIDS data
**Current Coverage:**
- ✅ Main database (teralinkx)
- ✅ RADIUS database
- ✅ HIDS database (basic)
- ✅ Redis data
- ✅ Docker volumes
- ✅ Configuration files
- ❌ HIDS models (ML models not backed up)
- ❌ HIDS logs (partial)
- ❌ HIDS configuration files

**Required Updates:**
1. Backup HIDS ML models (/app/models/)
2. Backup HIDS configuration files
3. Backup Suricata/Zeek configurations
4. Backup HIDS logs comprehensively
5. Add HIDS-specific restore instructions

---

### **4. restore.sh** ⚠️ **NEEDS HIDS INTEGRATION**
**Purpose:** Restore system from backup
**Status:** ⚠️ Partially complete - missing HIDS restore
**Current Coverage:**
- ✅ Main database restore
- ✅ RADIUS database restore
- ✅ HIDS database restore (basic)
- ✅ Redis data restore
- ✅ Docker volumes restore
- ❌ HIDS ML models restore
- ❌ HIDS configuration restore
- ❌ HIDS service validation

**Required Updates:**
1. Restore HIDS ML models
2. Restore HIDS configurations
3. Validate HIDS services after restore
4. Add HIDS health checks
5. Restart HIDS services in proper order

---

### **5. update.sh** ⚠️ **NEEDS HIDS INTEGRATION**
**Purpose:** Update system components safely
**Status:** ⚠️ Missing HIDS update logic
**Current Coverage:**
- ✅ Docker images update
- ✅ Application code update
- ✅ Dependencies update
- ✅ Database migrations
- ✅ Rolling restart
- ❌ HIDS services update
- ❌ ML model update/retrain
- ❌ HIDS configuration update

**Required Updates:**
1. Add HIDS services to update flow
2. Include ML model update option
3. Add HIDS database migrations
4. Update Suricata/Zeek rules
5. Restart HIDS services properly

---

### **6. deploy-production.sh** ✅ **FRONTEND ONLY - OK**
**Purpose:** Build and deploy frontend for production
**Status:** ✅ Complete (frontend-specific)
**Notes:** This is frontend-only, no HIDS integration needed

---

### **7. Other Scripts** ℹ️ **SPECIAL PURPOSE**

#### **deploy_auth_resilience.sh**
- Purpose: Deploy authentication resilience features
- Status: ✅ Specific feature deployment
- No HIDS integration needed

#### **deploy_fixes.sh**
- Purpose: Deploy specific fixes
- Status: ✅ Specific fix deployment
- No HIDS integration needed

#### **deploy-admin.sh**
- Purpose: Deploy admin panel
- Status: ✅ Admin-specific deployment
- No HIDS integration needed

#### **deploy-hotspot.sh**
- Purpose: Deploy hotspot features
- Status: ✅ Hotspot-specific deployment
- No HIDS integration needed

#### **setup_git_token.sh**
- Purpose: Configure Git authentication
- Status: ✅ Git configuration
- No HIDS integration needed

---

## 🔧 **Priority Updates Required**

### **HIGH PRIORITY**

#### **1. quick-install.sh**
```bash
# Add HIDS quick setup
ENABLE_HIDS_QUICK="n"  # Default off for quick install
if [[ $ENABLE_HIDS_QUICK == "y" ]]; then
    # Generate HIDS credentials
    HIDS_DB_PASSWORD=$(openssl rand -base64 12)
    
    # Create HIDS env files
    # Start HIDS services
fi

# Generate secure passwords
ADMIN_PASSWORD=$(openssl rand -base64 12)
DB_PASSWORD=$(openssl rand -base64 12)

# Save credentials to file
cat > credentials.txt << EOF
Admin: admin / $ADMIN_PASSWORD
Database: teralinkx / $DB_PASSWORD
EOF
```

#### **2. backup.sh**
```bash
# Add HIDS ML models backup
log "Backing up HIDS ML models..."
if [[ -d "hids/models" ]]; then
    cp -r hids/models/ "$BACKUP_DIR/hids_models/" 2>/dev/null || true
fi

# Backup HIDS configurations
log "Backing up HIDS configurations..."
cp -r hids/dashboard/.env "$BACKUP_DIR/configs/hids/" 2>/dev/null || true
cp -r hids/engine/.env "$BACKUP_DIR/configs/hids/" 2>/dev/null || true
cp -r hids/ml_service/.env "$BACKUP_DIR/configs/hids/" 2>/dev/null || true
cp -r hids/suricata/ "$BACKUP_DIR/configs/hids/" 2>/dev/null || true
cp -r hids/zeek/ "$BACKUP_DIR/configs/hids/" 2>/dev/null || true

# Backup HIDS logs
log "Backing up HIDS logs..."
cp -r hids/logs/ "$BACKUP_DIR/hids_logs/" 2>/dev/null || true
```

#### **3. restore.sh**
```bash
# Restore HIDS ML models
log "Restoring HIDS ML models..."
if [[ -d "$BACKUP_DIR/hids_models" ]]; then
    cp -r "$BACKUP_DIR/hids_models" hids/models/ 2>/dev/null || true
fi

# Restore HIDS configurations
log "Restoring HIDS configurations..."
if [[ -d "$BACKUP_DIR/configs/hids" ]]; then
    cp -r "$BACKUP_DIR/configs/hids/"* hids/ 2>/dev/null || true
fi

# Validate HIDS services
log "Validating HIDS services..."
if docker-compose ps ml_service | grep -q "Up"; then
    log "✅ ML Service is running"
else
    warn "❌ ML Service is not running"
fi
```

#### **4. update.sh**
```bash
# Add HIDS update option
echo "6. HIDS services update (ML models + rules)"
read -p "Enter choice (1-6): " UPDATE_TYPE

case $UPDATE_TYPE in
    6)
        log "Updating HIDS services..."
        UPDATE_HIDS=true
        ;;
esac

# Update HIDS services
if [[ $UPDATE_HIDS == true ]]; then
    log "Updating HIDS services..."
    
    # Update Suricata rules
    docker-compose exec suricata suricata-update
    
    # Restart HIDS services
    docker-compose restart ml_service hids_engine hids_dashboard
    
    # Optionally retrain ML model
    read -p "Retrain ML model? (y/n) [n]: " RETRAIN
    if [[ $RETRAIN == "y" ]]; then
        docker exec hids_jupyter python3 /home/jovyan/train_ml_proper.py
    fi
fi
```

---

## 📊 **Integration Status Summary**

| Script | Status | HIDS Integration | Priority |
|--------|--------|------------------|----------|
| install.sh | ✅ Complete | ✅ Full | - |
| quick-install.sh | ⚠️ Needs Update | ❌ None | 🔴 HIGH |
| backup.sh | ⚠️ Needs Update | ⚠️ Partial | 🔴 HIGH |
| restore.sh | ⚠️ Needs Update | ⚠️ Partial | 🔴 HIGH |
| update.sh | ⚠️ Needs Update | ❌ None | 🟡 MEDIUM |
| deploy-production.sh | ✅ Complete | N/A | - |
| deploy_auth_resilience.sh | ✅ Complete | N/A | - |
| deploy_fixes.sh | ✅ Complete | N/A | - |
| deploy-admin.sh | ✅ Complete | N/A | - |
| deploy-hotspot.sh | ✅ Complete | N/A | - |
| setup_git_token.sh | ✅ Complete | N/A | - |

---

## 🎯 **Recommended Action Plan**

### **Phase 1: Critical Updates (Do Now)**
1. ✅ Update quick-install.sh with HIDS support
2. ✅ Update backup.sh with HIDS data
3. ✅ Update restore.sh with HIDS restore

### **Phase 2: Enhancement Updates (Do Soon)**
4. ✅ Update update.sh with HIDS update logic
5. ✅ Add HIDS-specific health checks to all scripts
6. ✅ Create HIDS-specific deployment script

### **Phase 3: Documentation (Do After)**
7. ✅ Update all script documentation
8. ✅ Create troubleshooting guides
9. ✅ Add usage examples

---

## 📝 **Script Usage Guide**

### **For New Installation:**
```bash
# Full installation with all options
./scripts/deployment/install.sh

# Quick installation (minimal config)
./scripts/deployment/quick-install.sh
```

### **For Backup & Restore:**
```bash
# Create backup
./scripts/deployment/backup.sh

# Restore from backup
./scripts/deployment/restore.sh [backup_timestamp]
```

### **For Updates:**
```bash
# Update system
./scripts/deployment/update.sh
```

### **For Frontend Deployment:**
```bash
# Build and deploy frontend
cd TeralinkxFR
../scripts/deployment/deploy-production.sh
```

---

## 🐛 **Known Issues**

### **quick-install.sh**
- Hardcoded admin password (security risk)
- No HIDS support
- Missing health checks

### **backup.sh**
- HIDS ML models not backed up
- Incomplete HIDS configuration backup
- No backup verification

### **restore.sh**
- HIDS services not validated after restore
- ML models not restored
- No HIDS health checks

### **update.sh**
- No HIDS update logic
- ML model update not supported
- Suricata rules not updated

---

## ✅ **Next Steps**

1. **Implement quick-install.sh updates** - Add HIDS support and secure passwords
2. **Enhance backup.sh** - Include all HIDS data and models
3. **Improve restore.sh** - Add HIDS validation and health checks
4. **Update update.sh** - Add HIDS update capabilities
5. **Test all scripts** - Comprehensive testing with HIDS enabled
6. **Update documentation** - Reflect all changes in docs

---

**Status:** 📋 **ANALYSIS COMPLETE - READY FOR IMPLEMENTATION**

