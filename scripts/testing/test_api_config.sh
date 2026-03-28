#!/bin/bash

echo "🔍 Testing API Configuration - srv.teralinkx primary, service fallback"
echo "=================================================================="

# Test primary URL (srv.teralinkx)
echo "Testing primary URL: https://srv.teralinkxwaves.uk"
curl -s -o /dev/null -w "Primary Status: %{http_code} | Time: %{time_total}s\n" https://srv.teralinkxwaves.uk/api/health/ || echo "Primary: Connection failed"

echo ""

# Test fallback URL (service)
echo "Testing fallback URL: https://service.teralinkxwaves.uk"
curl -s -o /dev/null -w "Fallback Status: %{http_code} | Time: %{time_total}s\n" https://service.teralinkxwaves.uk/api/health/ || echo "Fallback: Connection failed"

echo ""
echo "✅ API configuration updated:"
echo "   - Primary: srv.teralinkxwaves.uk"
echo "   - Fallback: service.teralinkxwaves.uk"
echo "   - Auto-failover enabled in frontend"