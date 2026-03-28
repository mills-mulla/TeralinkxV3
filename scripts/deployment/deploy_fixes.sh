#!/bin/bash
# Quick deployment script for server restart fixes

set -e

echo "=========================================="
echo "TeralinkX Server Restart Fix Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: docker-compose.yml not found${NC}"
    echo "Please run this script from /home/ghost/Desktop/TeralinkxV3/teralinkx"
    exit 1
fi

echo -e "${YELLOW}Phase 1: Database Connection Fixes${NC}"
echo "This will:"
echo "  - Update database connection settings"
echo "  - Configure Redis connection pooling"
echo "  - Optimize Gunicorn worker recycling"
echo "  - Add connection cleanup middleware"
echo ""
read -p "Deploy Phase 1? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Deploying Phase 1...${NC}"
    
    # Restart services
    echo "Restarting services..."
    docker-compose restart web celery beat
    
    # Wait for services to start
    echo "Waiting for services to start..."
    sleep 10
    
    # Run tests
    echo -e "\n${GREEN}Running Phase 1 tests...${NC}"
    ./test_db_fixes.sh
    
    echo -e "\n${GREEN}Phase 1 deployed successfully!${NC}"
    echo "Monitor for 24 hours before deploying Phase 2"
    echo "Command: watch -n 60 'docker stats --no-stream teralinkx_web'"
fi

echo ""
echo -e "${YELLOW}Phase 2: Celery Async Payment Processing${NC}"
echo "This will:"
echo "  - Move M-Pesa API calls to Celery tasks"
echo "  - Eliminate Django worker blocking"
echo "  - Improve response time (15s → 0.1s)"
echo "  - Enable unlimited concurrent payments"
echo ""
read -p "Deploy Phase 2? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Deploying Phase 2...${NC}"
    
    # Test Celery first
    echo "Testing Celery setup..."
    ./test_celery_async.sh
    
    # Restart services
    echo "Restarting services..."
    docker-compose restart web celery
    
    # Wait for services to start
    echo "Waiting for services to start..."
    sleep 10
    
    echo -e "\n${GREEN}Phase 2 deployed successfully!${NC}"
    echo "Monitor first payment carefully"
    echo "Commands:"
    echo "  docker logs teralinkx_web -f | grep payment"
    echo "  docker logs teralinkx_celery -f"
fi

echo ""
echo "=========================================="
echo "Deployment Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Monitor memory: watch -n 60 'docker stats --no-stream teralinkx_web'"
echo "2. Check connections: docker exec teralinkx_web python manage.py check_db_connections"
echo "3. Monitor logs: docker logs teralinkx_web -f"
echo "4. Test payment: Make a test payment from frontend"
echo ""
echo "Documentation:"
echo "  - DB fixes: DB_CONNECTION_FIXES.md"
echo "  - Celery async: CELERY_ASYNC_DEPLOYMENT.md"
echo "  - Complete summary: COMPLETE_FIX_SUMMARY.md"
echo ""
echo -e "${GREEN}Good luck! 🚀${NC}"
