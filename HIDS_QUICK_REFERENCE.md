# HIDS MVP - Quick Reference Guide

## Start/Stop Commands

```bash
# Start all HIDS services
cd /home/ghost/Desktop/TeralinkxV3
./start_hids.sh

# Or manually:
docker compose up -d hids_engine hids_dashboard ml_service suricata

# Stop services
docker compose down

# View logs
docker logs -f hids_engine
docker logs -f hids_dashboard
```

## Access URLs

- **Dashboard**: http://localhost:5002
- **ML Service**: http://localhost:5001/health
- **Jupyter Notebooks**: http://localhost:8888

## API Endpoints

### Dashboard API (Port 5002)

```bash
# Hybrid alerts (fusion-scored)
curl http://localhost:5002/hybrid-alerts

# Raw Suricata alerts
curl http://localhost:5002/alerts

# Correlated alerts (5-tuple)
curl http://localhost:5002/correlated

# Statistics
curl http://localhost:5002/stats

# Top attack sources
curl http://localhost:5002/top-sources
```

### ML Service API (Port 5001)

```bash
# Health check
curl http://localhost:5001/health

# Predict anomaly
curl -X POST http://localhost:5001/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [80, 443, 1.5, 1024, 2048, 10, 1, 3]}'
```

## Testing

```bash
# Run MVP validation tests
cd /home/ghost/Desktop/TeralinkxV3
python3 hids/test_mvp.py

# Run integration tests
python3 hids/test_integration.py
```

## Understanding the Fusion Algorithm

### Composite Score Calculation
```
composite_score = (0.6 × signature_score) + (0.4 × ml_score)

Where:
- signature_score = (4 - suricata_severity) × 33.33
  - Severity 1 (high) → 100 points
  - Severity 2 (medium) → 50 points
  - Severity 3 (low) → 0 points

- ml_score = ml_confidence × 100 (if anomaly detected)
  - 0-100 scale based on ML model confidence
```

### Priority Assignment
- **CRITICAL**: Score ≥ 75 (High severity + High ML confidence)
- **HIGH**: Score ≥ 50 (High severity OR High ML confidence)
- **MEDIUM**: Score ≥ 25 (Medium severity + Medium ML confidence)
- **LOW**: Score < 25 (Low severity + Low ML confidence)

## Dashboard Features

### Hybrid Alerts Tab
- Shows fusion-scored alerts
- Color-coded priorities (Red=CRITICAL, Orange=HIGH, Yellow=MEDIUM, Green=LOW)
- Composite score badges
- Full explanations with ML insights

### Raw Alerts Tab
- Unprocessed Suricata alerts
- Useful for debugging

### Correlated Tab
- 5-tuple matched alerts
- Shows repeated attack patterns

## Key Files

```
hids/
├── engine/
│   ├── engine.py          # Core fusion algorithm
│   └── requirements.txt
├── ml_service/
│   ├── app.py            # ML prediction service
│   └── train.py          # Model training
├── dashboard/
│   ├── app.py            # Dashboard backend
│   └── templates/
│       └── index.html    # Dashboard UI
├── models/
│   ├── anomaly_detector.pkl  # Trained ML model
│   └── scaler.pkl
├── datasets/
│   └── *.csv             # CIC-IDS2017 data
└── test_mvp.py           # Validation tests
```

## Troubleshooting

### Service won't start
```bash
# Check logs
docker logs hids_engine

# Rebuild
docker compose build hids_engine
docker compose up -d hids_engine
```

### No alerts appearing
```bash
# Check if Suricata is running
docker compose ps suricata

# Check Suricata logs
docker logs hids_suricata

# Verify log file exists
docker exec hids_suricata ls -la /var/log/suricata/
```

### ML predictions failing
```bash
# Check ML service
curl http://localhost:5001/health

# Restart ML service
docker compose restart ml_service
```

### Database connection issues
```bash
# Check PostgreSQL
docker compose ps postgres

# View database logs
docker logs postgres
```

## Performance Tuning

### Adjust ML Model Sensitivity
Edit `hids/ml_service/app.py`:
```python
model = IsolationForest(
    contamination=0.1,  # Increase for more anomalies (0.1 = 10%)
    n_estimators=100    # Increase for better accuracy
)
```

### Adjust Fusion Weights
Edit `hids/engine/engine.py`:
```python
# Change from 60/40 to 70/30 (favor signatures more)
composite_score = (0.7 * normalized_sig_score) + (0.3 * ml_anomaly_score)
```

### Adjust Priority Thresholds
Edit `hids/engine/engine.py`:
```python
if composite_score >= 80:  # More strict CRITICAL threshold
    priority = 'CRITICAL'
```

## Monitoring

```bash
# Watch live alerts
docker logs -f hids_engine | grep "🎯"

# Monitor resource usage
docker stats hids_engine hids_dashboard ml_service

# Check alert counts
curl -s http://localhost:5002/stats | jq
```

## Backup & Recovery

```bash
# Backup database
docker exec postgres pg_dump -U hids hids > hids_backup.sql

# Restore database
docker exec -i postgres psql -U hids hids < hids_backup.sql

# Backup ML models
cp -r hids/models hids/models.backup
```

## Documentation

- Full MVP Spec: `hids/hidsmvp.docx`
- Deployment Guide: `HIDS_DEPLOYMENT.md`
- Implementation Summary: `HIDS_MVP_COMPLETE.md`
- Quick Reference: `HIDS_QUICK_REFERENCE.md`

## Support

For issues or questions:
1. Check logs: `docker logs hids_engine`
2. Run tests: `python3 hids/test_mvp.py`
3. Review documentation in `hids/` directory
