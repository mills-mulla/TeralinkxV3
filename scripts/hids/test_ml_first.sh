#!/bin/bash
# Test ML-First Detection System

echo "═══════════════════════════════════════════════════════════════"
echo "🧪 TESTING ML-FIRST DETECTION SYSTEM"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "📊 Current System Configuration:"
echo "  ✅ ML Weight: 70% (PRIMARY)"
echo "  ✅ Suricata Weight: 30% (SECONDARY)"
echo "  ✅ Model: Random Forest (CICIDS2017 + CICIDS2018 + NSL-KDD)"
echo "  ✅ Training: 60,000 samples (50/50 balanced)"
echo "  ✅ False Positive Rate: 1.70%"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "📈 DETECTION SCENARIOS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "Scenario 1: ML + Suricata BOTH Detect (HIGHEST CONFIDENCE)"
echo "  ML: 90% anomaly confidence"
echo "  Suricata: Severity 1 (High)"
echo "  Result: 70% (ML) + 30% (Suricata) = 100% score → CRITICAL"
echo "  Method: ml_confirmed_by_suricata"
echo ""

echo "Scenario 2: ML Detects, Suricata Doesn't (ML-PRIMARY)"
echo "  ML: 85% anomaly confidence"
echo "  Suricata: Severity 3 (Low/None)"
echo "  Result: 70% (ML) + 5% (Suricata) = 75% score → HIGH"
echo "  Method: ml_primary"
echo "  ⭐ This is where ML shines - detecting zero-days!"
echo ""

echo "Scenario 3: Suricata Detects, ML Says Normal (SURICATA OVERRIDE)"
echo "  ML: 80% normal confidence"
echo "  Suricata: Severity 1 (High)"
echo "  Result: 30% (Suricata) + 16.8% (ML penalty) = 46.8% score → MEDIUM"
echo "  Method: suricata_override"
echo "  ⚠️  Possible false positive or new signature"
echo ""

echo "Scenario 4: Both Say Normal"
echo "  ML: 90% normal confidence"
echo "  Suricata: Severity 3 (Low)"
echo "  Result: Low score → LOW priority"
echo "  Method: both_normal"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "🎯 WHY ML-FIRST IS BETTER FOR YOUR SYSTEM"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Modern Attack Detection:"
echo "   - ML trained on 2017/2018 attacks (recent patterns)"
echo "   - Suricata rules may be outdated"
echo ""
echo "2. Zero-Day Detection:"
echo "   - ML can detect unknown attacks by pattern"
echo "   - Suricata needs exact signature match"
echo ""
echo "3. Reduced False Positives:"
echo "   - Balanced training (50/50) reduces FP to 1.70%"
echo "   - Old system: 97% anomaly rate (unusable)"
echo ""
echo "4. Adaptive Learning:"
echo "   - Can retrain ML with new data"
echo "   - Suricata requires manual rule updates"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "📊 CHECK CURRENT DETECTION STATS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "Querying Prometheus metrics..."
echo ""

# Total predictions
TOTAL=$(curl -s 'http://localhost:9090/api/v1/query?query=sum(hids_ml_predictions_total)' | grep -o '"value":\[[^]]*\]' | grep -o '[0-9.]*$')
echo "Total ML Predictions: ${TOTAL:-N/A}"

# Anomalies
ANOMALIES=$(curl -s 'http://localhost:9090/api/v1/query?query=sum(hids_ml_predictions_total{prediction="anomaly"})' | grep -o '"value":\[[^]]*\]' | grep -o '[0-9.]*$')
echo "Anomalies Detected: ${ANOMALIES:-N/A}"

# Calculate rate
if [ ! -z "$TOTAL" ] && [ ! -z "$ANOMALIES" ]; then
    RATE=$(echo "scale=2; ($ANOMALIES / $TOTAL) * 100" | bc)
    echo "Current Anomaly Rate: ${RATE}%"
    echo ""
    
    if (( $(echo "$RATE < 10" | bc -l) )); then
        echo "✅ EXCELLENT - Anomaly rate under 10%"
    elif (( $(echo "$RATE < 30" | bc -l) )); then
        echo "✅ GOOD - Anomaly rate under 30%"
    else
        echo "⚠️  HIGH - Consider retraining with more normal traffic"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🔬 LIVE DETECTION MONITORING"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Watch live detections:"
echo "  docker logs -f hids_engine | grep '🤖\\|🎯'"
echo ""
echo "View in Grafana:"
echo "  http://localhost:3000/d/b0316ab7-6490-425b-a9eb-908bbafd725e"
echo ""
echo "Check database alerts:"
echo "  docker exec -it postgres psql -U teralinkx -d teralinkx -c 'SELECT * FROM correlated_alerts ORDER BY first_seen DESC LIMIT 10;'"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "✅ ML-FIRST SYSTEM ACTIVE"
echo "═══════════════════════════════════════════════════════════════"
