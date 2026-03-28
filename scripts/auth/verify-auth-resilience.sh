#!/bin/bash
# Verify auth resilience deployment

echo "🔍 Verifying Auth Resilience Deployment"
echo "======================================"

# Test backend status endpoint
echo "Testing backend status endpoint..."
if curl -s -f "http://localhost:8009/api/status/" | jq '.status' | grep -q "online"; then
    echo "✅ Backend status endpoint working"
else
    echo "❌ Backend status endpoint failed"
fi

# Test health check endpoint (requires auth)
echo "Testing health check endpoint..."
# This would require a valid token in production
echo "⚠️  Health check endpoint requires authentication"

# Check JWT secret persistence
echo "Checking JWT secret persistence..."
if [ -f "./data/jwt/jwt_secret.key" ]; then
    echo "✅ JWT secret file exists"
    echo "✅ JWT secret is $(wc -c < ./data/jwt/jwt_secret.key) characters"
else
    echo "❌ JWT secret file not found"
fi

# Check Redis connectivity
echo "Testing Redis connectivity..."
if docker-compose exec redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is responding"
else
    echo "❌ Redis connection failed"
fi

echo ""
echo "🎉 Auth Resilience Verification Complete"
