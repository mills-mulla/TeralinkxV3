#!/bin/bash
# Generate synthetic attack traffic for HIDS testing

echo "=== HIDS Traffic Generator ==="
echo "This will generate test attack traffic for Suricata/Zeek"
echo ""

TARGET="8.8.8.8"  # Google DNS (safe target)
INTERFACE="wlp2s0"

echo "1. Port Scan Simulation"
echo "   Scanning ports 20-25 on $TARGET"
for port in {20..25}; do
    timeout 1 nc -zv $TARGET $port 2>&1 | grep -v "timed out" &
done
wait
echo "   ✓ Port scan complete"
echo ""

echo "2. HTTP Flood Simulation (10 requests)"
for i in {1..10}; do
    curl -s http://example.com > /dev/null &
done
wait
echo "   ✓ HTTP flood complete"
echo ""

echo "3. DNS Query Flood (20 queries)"
for i in {1..20}; do
    dig @8.8.8.8 example.com > /dev/null &
done
wait
echo "   ✓ DNS flood complete"
echo ""

echo "Traffic generation complete!"
echo "Check Suricata logs: docker logs hids_suricata"
echo "Check alerts: curl http://localhost:5002/alerts"
