#!/bin/bash

echo "=========================================="
echo "Starting HIDS Stack"
echo "=========================================="

# Start core services
echo "Starting database and redis..."
docker compose up -d db redis

echo "Waiting for database to be healthy..."
sleep 10

# Start HIDS services
echo "Starting HIDS services..."
docker compose up -d hids_engine hids_dashboard ml_service

# Start network monitoring
echo "Starting Suricata and Zeek..."
docker compose up -d suricata zeek

echo ""
echo "=========================================="
echo "HIDS Stack Started"
echo "=========================================="
echo ""
echo "Services:"
echo "  - HIDS Dashboard: http://localhost:5002"
echo "  - ML Service:     http://localhost:5001"
echo "  - Grafana:        http://localhost:3000"
echo ""
echo "Check logs:"
echo "  docker logs -f hids_engine"
echo "  docker logs -f hids_dashboard"
echo "  docker logs -f ml_service"
echo ""
echo "Run tests:"
echo "  python3 hids/test_integration.py"
echo ""
