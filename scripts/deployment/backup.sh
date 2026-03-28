#!/bin/bash

# TeralinkX V3 - Backup Script
# Creates comprehensive backups of all data and configurations
# Author: TeralinkX Team

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKUP_ROOT="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════╗
║         TeralinkX V3 Backup           ║
║       Data Protection System         ║
╚═══════════════════════════════════════╝
EOF
echo -e "${NC}"

log "Starting backup process..."
log "Backup directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"/{database,volumes,configs,logs}

cd "$PROJECT_ROOT"

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    warn "Some services may not be running. Backup may be incomplete."
fi

# Backup databases
log "Backing up databases..."
if docker-compose exec -T db pg_isready -U teralinkx &>/dev/null; then
    docker-compose exec -T db pg_dump -U teralinkx teralinkx > "$BACKUP_DIR/database/teralinkx.sql"
    docker-compose exec -T db pg_dump -U radius_user radius_db > "$BACKUP_DIR/database/radius_db.sql" 2>/dev/null || true
    docker-compose exec -T db pg_dump -U hids hids > "$BACKUP_DIR/database/hids.sql" 2>/dev/null || true
    log "Database backup completed"
else
    warn "Database not accessible. Skipping database backup."
fi

# Backup Redis data
log "Backing up Redis data..."
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    docker-compose exec -T redis redis-cli BGSAVE
    sleep 5
    docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/database/redis_dump.rdb" 2>/dev/null || warn "Redis backup failed"
else
    warn "Redis not accessible. Skipping Redis backup."
fi

# Backup Docker volumes
log "Backing up Docker volumes..."
docker run --rm -v teralinkxv3_pg_data:/data -v "$BACKUP_DIR/volumes":/backup alpine tar czf /backup/pg_data.tar.gz -C /data . 2>/dev/null || warn "PostgreSQL volume backup failed"
docker run --rm -v teralinkxv3_grafana_data:/data -v "$BACKUP_DIR/volumes":/backup alpine tar czf /backup/grafana_data.tar.gz -C /data . 2>/dev/null || warn "Grafana volume backup failed"
docker run --rm -v teralinkxv3_prometheus_data:/data -v "$BACKUP_DIR/volumes":/backup alpine tar czf /backup/prometheus_data.tar.gz -C /data . 2>/dev/null || warn "Prometheus volume backup failed"
docker run --rm -v teralinkxv3_loki_data:/data -v "$BACKUP_DIR/volumes":/backup alpine tar czf /backup/loki_data.tar.gz -C /data . 2>/dev/null || warn "Loki volume backup failed"

# Backup configuration files
log "Backing up configuration files..."
cp -r nginx/ "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r certbot/ "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r cloudflared/ "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r freeradius/ "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r monitoring/ "$BACKUP_DIR/configs/" 2>/dev/null || true
cp docker-compose.yml "$BACKUP_DIR/configs/" 2>/dev/null || true
find . -name ".env" -exec cp {} "$BACKUP_DIR/configs/" \; 2>/dev/null || true

# Backup application data
log "Backing up application data..."
cp -r teralinkx/media/ "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r radius_api/media/ "$BACKUP_DIR/configs/" 2>/dev/null || true
cp -r data/ "$BACKUP_DIR/configs/" 2>/dev/null || true

# Backup HIDS data
log "Backing up HIDS data..."
mkdir -p "$BACKUP_DIR/hids"
cp -r hids/models/ "$BACKUP_DIR/hids/" 2>/dev/null || true
cp -r hids/dashboard/.env "$BACKUP_DIR/hids/" 2>/dev/null || true
cp -r hids/engine/.env "$BACKUP_DIR/hids/" 2>/dev/null || true
cp -r hids/ml_service/.env "$BACKUP_DIR/hids/" 2>/dev/null || true
cp -r hids/suricata/ "$BACKUP_DIR/hids/" 2>/dev/null || true
cp -r hids/zeek/ "$BACKUP_DIR/hids/" 2>/dev/null || true
cp -r hids/pcaps/ "$BACKUP_DIR/hids/" 2>/dev/null || true

# Backup logs
log "Backing up logs..."
docker-compose logs --no-color > "$BACKUP_DIR/logs/docker-compose.log" 2>/dev/null || true
cp -r hids/logs/ "$BACKUP_DIR/logs/" 2>/dev/null || true

# Create backup manifest
log "Creating backup manifest..."
cat > "$BACKUP_DIR/manifest.txt" << EOF
TeralinkX V3 Backup Manifest
Created: $(date)
Backup ID: $TIMESTAMP
Project Root: $PROJECT_ROOT

=== BACKUP CONTENTS ===
database/
  - teralinkx.sql (Main application database)
  - radius_db.sql (RADIUS database)
  - hids.sql (HIDS database)
  - redis_dump.rdb (Redis data)

volumes/
  - pg_data.tar.gz (PostgreSQL data volume)
  - grafana_data.tar.gz (Grafana data volume)
  - prometheus_data.tar.gz (Prometheus data volume)
  - loki_data.tar.gz (Loki data volume)

configs/
  - nginx/ (Nginx configuration)
  - certbot/ (SSL certificates)
  - cloudflared/ (Cloudflare tunnel)
  - freeradius/ (RADIUS server config)
  - monitoring/ (Monitoring stack config)
  - docker-compose.yml (Service orchestration)
  - .env files (Environment variables)
  - media/ (Uploaded files)
  - data/ (Application data)

hids/
  - models/ (ML models and scalers)
  - dashboard/.env (Dashboard configuration)
  - engine/.env (Engine configuration)
  - ml_service/.env (ML service configuration)
  - suricata/ (Suricata IDS configuration)
  - zeek/ (Zeek network monitor configuration)
  - pcaps/ (Packet capture files)

logs/
  - docker-compose.log (Service logs)
  - hids/ (HIDS logs)

=== RESTORE INSTRUCTIONS ===
1. Stop all services: docker-compose down
2. Restore databases: psql -U teralinkx -d teralinkx < database/teralinkx.sql
3. Restore volumes: tar xzf volumes/pg_data.tar.gz -C /var/lib/docker/volumes/teralinkxv3_pg_data/_data/
4. Restore configs: cp -r configs/* /path/to/project/
5. Start services: docker-compose up -d

=== BACKUP SIZE ===
$(du -sh "$BACKUP_DIR" | cut -f1)
EOF

# Calculate backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

# Compress backup (optional)
read -p "Compress backup? (y/n) [n]: " COMPRESS
if [[ $COMPRESS == "y" ]]; then
    log "Compressing backup..."
    cd "$BACKUP_ROOT"
    tar czf "${TIMESTAMP}.tar.gz" "$TIMESTAMP"
    rm -rf "$TIMESTAMP"
    BACKUP_PATH="$BACKUP_ROOT/${TIMESTAMP}.tar.gz"
    BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)
else
    BACKUP_PATH="$BACKUP_DIR"
fi

# Cleanup old backups (keep last 5)
log "Cleaning up old backups..."
cd "$BACKUP_ROOT"
ls -t | tail -n +6 | xargs rm -rf 2>/dev/null || true

log "✅ Backup completed successfully!"
echo
echo -e "${BLUE}=== BACKUP SUMMARY ===${NC}"
echo -e "Backup Path: $BACKUP_PATH"
echo -e "Backup Size: $BACKUP_SIZE"
echo -e "Timestamp: $TIMESTAMP"
echo
echo -e "${YELLOW}💡 To restore from this backup:${NC}"
echo -e "./scripts/deployment/restore.sh $TIMESTAMP"
echo