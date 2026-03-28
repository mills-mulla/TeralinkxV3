#!/bin/bash

# TeralinkX V3 - Update Script
# Updates system components safely
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
║         TeralinkX V3 Update           ║
║       System Update Manager          ║
╚═══════════════════════════════════════╝
EOF
echo -e "${NC}"

cd "$PROJECT_ROOT"

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    warn "Some services are not running. Starting services first..."
    docker-compose up -d
    sleep 10
fi

# Create backup before update
log "Creating backup before update..."
if [[ -f "scripts/deployment/backup.sh" ]]; then
    ./scripts/deployment/backup.sh
else
    warn "Backup script not found. Proceeding without backup."
fi

# Update options
echo -e "${YELLOW}Select update type:${NC}"
echo "1. Full update (images + code + dependencies)"
echo "2. Images only (Docker images)"
echo "3. Code only (application code)"
echo "4. Dependencies only (npm/pip packages)"
echo "5. Database migrations only"
echo "6. HIDS services update (ML models + IDS rules)"
read -p "Enter choice (1-6): " UPDATE_TYPE

case $UPDATE_TYPE in
    1)
        log "Performing full update..."
        UPDATE_IMAGES=true
        UPDATE_CODE=true
        UPDATE_DEPS=true
        UPDATE_DB=true
        ;;
    2)
        log "Updating Docker images only..."
        UPDATE_IMAGES=true
        UPDATE_CODE=false
        UPDATE_DEPS=false
        UPDATE_DB=false
        ;;
    3)
        log "Updating application code only..."
        UPDATE_IMAGES=false
        UPDATE_CODE=true
        UPDATE_DEPS=false
        UPDATE_DB=true
        ;;
    4)
        log "Updating dependencies only..."
        UPDATE_IMAGES=false
        UPDATE_CODE=false
        UPDATE_DEPS=true
        UPDATE_DB=false
        ;;
    5)
        log "Running database migrations only..."
        UPDATE_IMAGES=false
        UPDATE_CODE=false
        UPDATE_DEPS=false
        UPDATE_DB=true
        UPDATE_HIDS=false
        ;;
    6)
        log "Updating HIDS services..."
        UPDATE_IMAGES=false
        UPDATE_CODE=false
        UPDATE_DEPS=false
        UPDATE_DB=false
        UPDATE_HIDS=true
        ;;
    *)
        error "Invalid choice"
        ;;
esac

# Update Docker images
if [[ $UPDATE_IMAGES == true ]]; then
    log "Pulling latest Docker images..."
    docker-compose pull
    
    log "Rebuilding custom images..."
    docker-compose build --no-cache
fi

# Update application code
if [[ $UPDATE_CODE == true ]]; then
    log "Updating application code..."
    
    # Git pull if in git repository
    if [[ -d ".git" ]]; then
        log "Pulling latest code from repository..."
        git pull origin main || git pull origin master || warn "Git pull failed"
    fi
    
    # Collect static files
    log "Collecting static files..."
    docker-compose exec -T web python manage.py collectstatic --noinput
fi

# Update dependencies
if [[ $UPDATE_DEPS == true ]]; then
    log "Updating dependencies..."
    
    # Update Python dependencies
    if [[ -f "requirements.txt" ]]; then
        log "Updating Python dependencies..."
        docker-compose exec -T web pip install -r requirements.txt --upgrade
    fi
    
    # Update frontend dependencies
    if [[ -f "TeralinkxFR/package.json" ]] && command -v npm &> /dev/null; then
        log "Updating frontend dependencies..."
        cd TeralinkxFR
        npm update
        npm run build:production
        cd ..
    fi
fi

# Database migrations
if [[ $UPDATE_DB == true ]]; then
    log "Running database migrations..."
    docker-compose exec -T web python manage.py migrate
    
    # Update RADIUS database if needed
    docker-compose exec -T radius_api python manage.py migrate 2>/dev/null || true
    
    # Update HIDS database if needed
    if docker-compose ps hids_engine 2>/dev/null | grep -q "Up"; then
        log "Running HIDS database migrations..."
        # HIDS uses schema.sql, check if updates needed
        docker-compose exec -T hids_engine python -c "from engine import init_schema; init_schema()" 2>/dev/null || true
    fi
fi

# Update HIDS services
if [[ $UPDATE_HIDS == true ]]; then
    log "Updating HIDS services..."
    
    # Check if HIDS is enabled
    if ! docker-compose ps ml_service 2>/dev/null | grep -q "Up"; then
        warn "HIDS services are not running. Skipping HIDS update."
    else
        # Update Suricata rules
        log "Updating Suricata IDS rules..."
        if docker-compose ps suricata | grep -q "Up"; then
            docker-compose exec -T suricata suricata-update 2>/dev/null || warn "Suricata update failed"
            docker-compose restart suricata
            log "✅ Suricata rules updated"
        fi
        
        # Update Zeek scripts (if custom scripts exist)
        log "Checking Zeek scripts..."
        if [[ -d "hids/zeek/scripts" ]]; then
            log "Zeek custom scripts found - restart Zeek to apply"
            docker-compose restart zeek
        fi
        
        # Check ML model status
        log "Checking ML model status..."
        if docker-compose exec -T ml_service ls /app/models/anomaly_detector.pkl &>/dev/null; then
            log "✅ ML model exists"
            
            # Ask if user wants to retrain
            read -p "Retrain ML model with latest data? (y/n) [n]: " RETRAIN_ML
            if [[ $RETRAIN_ML == "y" ]]; then
                log "Starting ML model training..."
                log "This may take 10-30 minutes depending on dataset size"
                
                if docker-compose ps jupyter | grep -q "Up"; then
                    docker exec hids_jupyter python3 /home/jovyan/train_ml_proper.py || warn "ML training failed"
                    log "✅ ML model retrained"
                    
                    # Restart ML service to load new model
                    docker-compose restart ml_service
                    log "✅ ML service restarted with new model"
                else
                    warn "Jupyter service not running. Cannot retrain model."
                fi
            fi
        else
            warn "No ML model found. Train model with: docker exec hids_jupyter python3 /home/jovyan/train_ml_proper.py"
        fi
        
        # Restart HIDS services
        log "Restarting HIDS services..."
        docker-compose restart hids_engine hids_dashboard
        
        # Wait for services to be ready
        sleep 10
        
        # HIDS health checks
        log "Performing HIDS health checks..."
        
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
        
        log "✅ HIDS services updated successfully"
    fi
fi

# Restart services with zero downtime
log "Restarting services..."

# Rolling restart for zero downtime
services=("web" "celery" "celery_beat" "radius_api")

# Add HIDS services if they're running
if docker-compose ps ml_service 2>/dev/null | grep -q "Up" && [[ $UPDATE_HIDS != true ]]; then
    services+=("ml_service" "hids_engine" "hids_dashboard")
fi

for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        log "Restarting $service..."
        docker-compose restart "$service"
        sleep 5
    fi
done

# Restart nginx last
docker-compose restart nginx

# Health checks
log "Performing health checks..."
sleep 10

# Check database
if docker-compose exec -T db pg_isready -U teralinkx &>/dev/null; then
    log "✅ Database is healthy"
else
    warn "❌ Database health check failed"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    log "✅ Redis is healthy"
else
    warn "❌ Redis health check failed"
fi

# Check web service
if docker-compose exec -T web python manage.py check &>/dev/null; then
    log "✅ Django application is healthy"
else
    warn "❌ Django application health check failed"
fi

# Check nginx
if docker-compose exec -T nginx nginx -t &>/dev/null; then
    log "✅ Nginx configuration is valid"
else
    warn "❌ Nginx configuration check failed"
fi

# Test API endpoints
log "Testing API endpoints..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ | grep -q "200"; then
    log "✅ API health endpoint is responding"
else
    warn "❌ API health endpoint check failed"
fi

# Check HIDS services if running
if docker-compose ps ml_service 2>/dev/null | grep -q "Up"; then
    log "Checking HIDS services..."
    
    if curl -s http://localhost:5001/health | grep -q "healthy" 2>/dev/null; then
        log "✅ ML Service is healthy"
    else
        warn "❌ ML Service health check failed"
    fi
    
    if curl -s http://localhost:5002/api | grep -q "HIDS" 2>/dev/null; then
        log "✅ HIDS Dashboard is healthy"
    else
        warn "❌ HIDS Dashboard health check failed"
    fi
fi

# Clean up old Docker images
read -p "Clean up old Docker images? (y/n) [y]: " CLEANUP
CLEANUP=${CLEANUP:-y}
if [[ $CLEANUP == "y" ]]; then
    log "Cleaning up old Docker images..."
    docker image prune -f
    docker system prune -f --volumes
fi

# Generate update report
log "Generating update report..."
cat > "update_report_$(date +%Y%m%d_%H%M%S).txt" << EOF
TeralinkX V3 Update Report
Generated on: $(date)

=== UPDATE SUMMARY ===
Update Type: $UPDATE_TYPE
Images Updated: $UPDATE_IMAGES
Code Updated: $UPDATE_CODE
Dependencies Updated: $UPDATE_DEPS
Database Migrated: $UPDATE_DB
HIDS Updated: ${UPDATE_HIDS:-false}

=== SERVICES STATUS ===
$(docker-compose ps)

=== DOCKER IMAGES ===
$(docker-compose images)

=== SYSTEM INFO ===
Docker Version: $(docker --version)
Docker Compose Version: $(docker-compose --version)
Available Disk Space: $(df -h . | awk 'NR==2 {print $4}')
Available Memory: $(free -h | awk 'NR==2{print $7}')

=== NEXT STEPS ===
1. Monitor application logs: docker-compose logs -f
2. Test all functionality thoroughly
3. Monitor system performance
4. Check for any error messages

=== ROLLBACK INSTRUCTIONS ===
If issues occur, restore from backup:
./scripts/deployment/restore.sh [backup_timestamp]
EOF

log "✅ Update completed successfully!"
echo
echo -e "${BLUE}=== UPDATE SUMMARY ===${NC}"
echo -e "Update Type: $(case $UPDATE_TYPE in 1) echo 'Full Update';; 2) echo 'Images Only';; 3) echo 'Code Only';; 4) echo 'Dependencies Only';; 5) echo 'Database Only';; 6) echo 'HIDS Services';; esac)"
echo -e "Services Status:"
docker-compose ps
echo
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "1. Monitor logs: docker-compose logs -f"
echo -e "2. Test application functionality"
echo -e "3. Check update report: ls -la update_report_*.txt"
echo
echo -e "${GREEN}🎉 TeralinkX V3 has been updated successfully!${NC}"