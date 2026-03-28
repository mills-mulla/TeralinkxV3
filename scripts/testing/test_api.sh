#!/bin/bash

# Test API endpoints with JWT authentication

# 1. Login to get token
echo "=== Getting JWT Token ==="
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8009/suapi/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}')

echo "$TOKEN_RESPONSE" | python3 -m json.tool

# Extract access token
ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Failed to get access token"
    exit 1
fi

echo -e "\n=== Testing Packages API ==="
curl -s http://localhost:8009/suapi/packages/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool | head -80

echo -e "\n=== Testing Clients API ==="
curl -s http://localhost:8009/suapi/clients/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool | head -80

echo -e "\n=== Testing Locations API ==="
curl -s http://localhost:8009/suapi/locations/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool | head -50
