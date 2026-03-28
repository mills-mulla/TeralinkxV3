#!/bin/bash
# Health monitoring script for auth resilience

BACKEND_URL="http://localhost:8009"
LOG_FILE="/var/log/teralinkx/auth-health.log"

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check backend status
    if curl -s -f "${BACKEND_URL}/api/status/" > /dev/null; then
        echo "[$timestamp] Backend healthy" >> "$LOG_FILE"
    else
        echo "[$timestamp] Backend unhealthy - potential restart detected" >> "$LOG_FILE"
        # Could trigger additional recovery actions here
    fi
    
    sleep 60
done
