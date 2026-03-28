#!/bin/bash

# TeralinkX V3 - Restore Script
# Restores system from backup
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
║         TeralinkX V3 Restore          ║
║       Data Recovery System           ║
╚═══════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if backup ID provided
if [[ -z "$1" ]]; then
    echo -e "${YELLOW}Available backups:${NC}"
    ls -la "$BACKUP_ROOT" 2>/dev/null | grep -E '^d' | awk '{print $9}' | grep -E '^[0-9]' || echo "No backups found"
    echo
    read -p "Enter backup ID (timestamp): " BACKUP_ID
else
    BACKUP_ID="$1"
fi

# Determine backup path
if [[ -f "$BACKUP_ROOT/${BACKUP_ID}.tar.gz" ]]; then
    BACKUP_PATH="$BACKUP_ROOT/${BACKUP_ID}.tar.gz"
    COMPRESSED=true
elif [[ -d "$BACKUP_ROOT/$BACKUP_ID" ]]; then
    BACKUP_PATH="$BACKUP_ROOT/$BACKUP_ID"
    COMPRESSED=false
else
    error "Backup not found: $BACKUP_ID"
fi

log "Found backup: $BACKUP_PATH"

# Extract compressed backup if needed
if [[ $COMPRESSED == true ]]; then
    log "Extracting compressed backup..."
    cd "$BACKUP_ROOT"
    tar xzf "${BACKUP_ID}.tar.gz"
    BACKUP_DIR="$BACKUP_ROOT/$BACKUP_ID"
else
    BACKUP_DIR="$BACKUP_PATH"
fi

# Verify backup integrity
if [[ ! -f "$BACKUP_DIR/manifest.txt" ]]; then
    error "Invalid backup: manifest.txt not found"
fi

log "Backup manifest:"
cat "$BACKUP_DIR/manifest.txt"
echo

# Confirmation
read -p "⚠️  This will overwrite current data. Continue? (y/N): " CONFIRM
if [[ $CONFIRM != "y" ]]; then
    log "Restore cancelled"
    exit 0
fi

cd "$PROJECT_ROOT"

# Stop services
log "Stopping services..."
docker-compose down --volumes

# Restore configuration files
log "Restoring configuration files..."
if [[ -d "$BACKUP_DIR/configs" ]]; then
    cp -r "$BACKUP_DIR/configs/nginx" . 2>/dev/null || true
    cp -r "$BACKUP_DIR/configs/certbot" . 2>/dev/null || true
    cp -r "$BACKUP_DIR/configs/cloudflared" . 2>/dev/null || true
    cp -r "$BACKUP_DIR/configs/freeradius" . 2>/dev/null || true
    cp -r "$BACKUP_DIR/configs/monitoring" . 2>/dev/null || true
    cp "$BACKUP_DIR/configs/docker-compose.yml" . 2>/dev/null || true
    
    # Restore .env files
    find "$BACKUP_DIR/configs" -name ".env" -exec cp {} . \; 2>/dev/null || true
    find "$BACKUP_DIR/configs" -name ".env" -exec basename {} \; | while read env_file; do
        if [[ -f "$BACKUP_DIR/configs/$env_file" ]]; then
            # Determine target directory based on env file
            case "$env_file" in
                ".env") cp "$BACKUP_DIR/configs/$env_file" . ;;
                *) find . -name "$env_file" -exec cp "$BACKUP_DIR/configs/$env_file" {} \; ;;
            esac
        fi
    done
    
    # Restore media files
    cp -r "$BACKUP_DIR/configs/media" teralinkx/ 2>/dev/null || true
    cp -r "$BACKUP_DIR/configs/media" radius_api/ 2>/dev/null || true
    cp -r "$BACKUP_DIR/configs/data" . 2>/dev/null || true
    
    # Restore HIDS data
    if [[ -d "$BACKUP_DIR/hids" ]]; then
        log "Restoring HIDS data..."
        cp -r "$BACKUP_DIR/hids/models" hids/ 2>/dev/null || true
        cp "$BACKUP_DIR/hids/dashboard/.env" hids/dashboard/ 2>/dev/null || true
        cp "$BACKUP_DIR/hids/engine/.env" hids/engine/ 2>/dev/null || true
        cp "$BACKUP_DIR/hids/ml_service/.env" hids/ml_service/ 2>/dev/null || true
        cp -r "$BACKUP_DIR/hids/suricata" hids/ 2>/dev/null || true
        cp -r "$BACKUP_DIR/hids/zeek" hids/ 2>/dev/null || true
        cp -r "$BACKUP_DIR/hids/pcaps" hids/ 2>/dev/null || true
    fi
fi

# Start database service
log "Starting database service..."
docker-compose up -d db
sleep 10

# Wait for database
log "Waiting for database to be ready..."
timeout=60
while ! docker-compose exec -T db pg_isready -U teralinkx &>/dev/null; do
    sleep 2
    timeout=$((timeout - 2))
    if [[ $timeout -le 0 ]]; then
        error "Database failed to start"
    fi
done

# Restore databases
log "Restoring databases..."
if [[ -f "$BACKUP_DIR/database/teralinkx.sql" ]]; then
    docker-compose exec -T db dropdb -U teralinkx teralinkx --if-exists
    docker-compose exec -T db createdb -U teralinkx teralinkx
    docker-compose exec -T db psql -U teralinkx -d teralinkx < "$BACKUP_DIR/database/teralinkx.sql"
    log "Main database restored"
fi

if [[ -f "$BACKUP_DIR/database/radius_db.sql" ]]; then
    docker-compose exec -T db dropdb -U teralinkx radius_db --if-exists
    docker-compose exec -T db createdb -U teralinkx radius_db
    docker-compose exec -T db psql -U teralinkx -d radius_db < "$BACKUP_DIR/database/radius_db.sql"
    log "RADIUS database restored"
fi

if [[ -f "$BACKUP_DIR/database/hids.sql" ]]; then
    docker-compose exec -T db dropdb -U teralinkx hids --if-exists
    docker-compose exec -T db createdb -U teralinkx hids
    docker-compose exec -T db psql -U teralinkx -d hids < "$BACKUP_DIR/database/hids.sql"
    log "HIDS database restored"
fi

# Start Redis
log "Starting Redis service..."
docker-compose up -d redis
sleep 5

# Restore Redis data
if [[ -f "$BACKUP_DIR/database/redis_dump.rdb" ]]; then
    log "Restoring Redis data..."
    docker-compose stop redis
    docker cp "$BACKUP_DIR/database/redis_dump.rdb" $(docker-compose ps -q redis):/data/dump.rdb 2>/dev/null || warn "Redis restore failed"
    docker-compose start redis
fi

# Restore Docker volumes
log "Restoring Docker volumes..."
if [[ -f "$BACKUP_DIR/volumes/pg_data.tar.gz" ]]; then
    docker run --rm -v teralinkxv3_pg_data:/data -v "$BACKUP_DIR/volumes":/backup alpine sh -c "cd /data && tar xzf /backup/pg_data.tar.gz" 2>/dev/null || warn "PostgreSQL volume restore failed"
fi

if [[ -f "$BACKUP_DIR/volumes/grafana_data.tar.gz" ]]; then
    docker run --rm -v teralinkxv3_grafana_data:/data -v "$BACKUP_DIR/volumes":/backup alpine sh -c "cd /data && tar xzf /backup/grafana_data.tar.gz" 2>/dev/null || warn "Grafana volume restore failed"
fi

if [[ -f "$BACKUP_DIR/volumes/prometheus_data.tar.gz" ]]; then
    docker run --rm -v teralinkxv3_prometheus_data:/data -v "$BACKUP_DIR/volumes":/backup alpine sh -c "cd /data && tar xzf /backup/prometheus_data.tar.gz" 2>/dev/null || warn "Prometheus volume restore failed"
fi

if [[ -f "$BACKUP_DIR/volumes/loki_data.tar.gz" ]]; then
    docker run --rm -v teralinkxv3_loki_data:/data -v "$BACKUP_DIR/volumes":/backup alpine sh -c "cd /data && tar xzf /backup/loki_data.tar.gz" 2>/dev/null || warn "Loki volume restore failed"
fi

# Start all services
log "Starting all services..."
docker-compose up -d

# Wait for services to be ready
log "Waiting for services to be ready..."
sleep 30

# Run migrations (in case of schema changes)
log "Running database migrations..."
docker-compose exec -T web python manage.py migrate --run-syncdb

# Collect static files
log "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Health check
log "Performing health checks..."
if docker-compose exec -T db pg_isready -U teralinkx &>/dev/null; then
    log "✅ Database is healthy"
else
    warn "❌ Database health check failed"
fi

if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    log "✅ Redis is healthy"
else
    warn "❌ Redis health check failed"
fi

if docker-compose exec -T web python manage.py check &>/dev/null; then
    log "✅ Django application is healthy"
else
    warn "❌ Django application health check failed"
fi

# Check HIDS services if they exist
if docker-compose ps ml_service 2>/dev/null | grep -q "Up"; then
    log "Checking HIDS services..."
    
    if curl -s http://localhost:5001/health | grep -q "healthy" 2>/dev/null; then
        log "✅ ML Service is healthy"
    else
        warn "❌ ML Service health check failed"
    fi
    
    if docker-compose ps hids_engine | grep -q "Up"; then
        log "✅ HIDS Engine is running"
    else
        warn "❌ HIDS Engine is not running"
    fi
    
    if curl -s http://localhost:5002/api | grep -q "HIDS" 2>/dev/null; then
        log "✅ HIDS Dashboard is healthy"
    else
        warn "❌ HIDS Dashboard health check failed"
    fi
fi

# Cleanup extracted backup if it was compressed
if [[ $COMPRESSED == true ]]; then
    rm -rf "$BACKUP_DIR"
fi

log "✅ Restore completed successfully!"
echo
echo -e "${BLUE}=== RESTORE SUMMARY ===${NC}"
echo -e "Restored from: $BACKUP_PATH"
echo -e "Backup ID: $BACKUP_ID"
echo -e "Services status:"
docker-compose ps
echo
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "1. Verify all services are running correctly"
echo -e "2. Test application functionality"
echo -e "3. Check logs for any issues: docker-compose logs"
echo