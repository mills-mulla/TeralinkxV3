#!/bin/bash
# Test script to verify database connection fixes

echo "==================================="
echo "Database Connection Fix Verification"
echo "==================================="
echo ""

echo "1. Checking Gunicorn configuration..."
docker logs teralinkx_web --tail 30 | grep -E "Starting Gunicorn|Worker recycling|Timeout"
echo ""

echo "2. Checking current memory usage..."
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep teralinkx_web
echo ""

echo "3. Checking PostgreSQL connections..."
docker exec postgres psql -U teralinkx -d teralinkx -c "SELECT count(*) as total, state FROM pg_stat_activity WHERE datname='teralinkx' GROUP BY state;" 2>/dev/null || echo "Note: Run with correct postgres user"
echo ""

echo "4. Checking Redis connections..."
docker exec redis redis-cli INFO clients | grep connected_clients
echo ""

echo "5. Checking for long-running queries..."
docker exec postgres psql -U teralinkx -d teralinkx -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '10 seconds';" 2>/dev/null || echo "Note: Run with correct postgres user"
echo ""

echo "6. Testing database connection health command..."
docker exec teralinkx_web python manage.py check_db_connections 2>&1 | head -20
echo ""

echo "==================================="
echo "Verification Complete"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Monitor memory: watch -n 60 'docker stats --no-stream teralinkx_web'"
echo "2. Check logs: docker logs teralinkx_web -f"
echo "3. Monitor for 24 hours before declaring success"
