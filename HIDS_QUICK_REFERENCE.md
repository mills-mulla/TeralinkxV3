# HIDS Stack - Quick Reference

## ✅ Added Services

| Service | Container | Port | Access URL |
|---------|-----------|------|------------|
| Suricata | hids_suricata | - | host network |
| Zeek | hids_zeek | - | host network |
| TCPReplay | hids_tcpreplay | - | host network |
| Jupyter | hids_jupyter | 8888 | http://localhost:8888 |
| ML Service | hids_ml_service | 5001 | https://teralinkxwaves.uk/ml/ |
| HIDS Engine | hids_engine | - | background service |
| Dashboard | hids_dashboard | 5002 | https://teralinkxwaves.uk/hids/ |
| HIDS DB | hids_postgres | 5433 | localhost:5433 |

## 📁 Directory Structure

```
hids/
├── dashboard/          # Flask dashboard
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── engine/            # Correlation engine
│   ├── engine.py
│   ├── Dockerfile
│   └── requirements.txt
├── ml_service/        # ML prediction API
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── suricata/          # IDS config
│   ├── logs/
│   ├── rules/
│   └── suricata.yaml
├── zeek/              # Flow analysis
│   ├── logs/
│   └── scripts/
├── pcaps/             # Packet captures
├── notebooks/         # Jupyter notebooks
├── datasets/          # Training data
└── models/            # Trained ML models
```

## 🚀 Commands

```bash
# Start all HIDS services
docker-compose up -d suricata zeek hids_db hids_engine hids_dashboard ml_service jupyter

# Start only specific services
docker-compose up -d hids_dashboard ml_service

# View logs
docker-compose logs -f hids_engine
docker-compose logs -f suricata

# Stop HIDS services
docker-compose stop suricata zeek hids_engine hids_dashboard ml_service jupyter

# Restart a service
docker-compose restart hids_engine
```

## 🔧 Configuration

### Suricata
- Config: `./hids/suricata/suricata.yaml`
- Rules: `./hids/suricata/rules/suricata.rules`
- Logs: `./hids/suricata/logs/eve.json`

### Zeek
- Scripts: `./hids/zeek/scripts/`
- Logs: `./hids/zeek/logs/`

### Network Interface
Update interface in configs (default: eth0):
```bash
ip link show  # Check your interface name
```

## 🔗 Integration Points

1. **Suricata → HIDS Engine**: Reads `/data/suricata/eve.json`
2. **Zeek → HIDS Engine**: Reads `/data/zeek/*.log`
3. **HIDS Engine → Redis**: Buffers events
4. **HIDS Engine → PostgreSQL**: Stores alerts
5. **Dashboard → PostgreSQL**: Displays alerts
6. **ML Service → Models**: Loads from `/app/models/`

## 📊 Database Schema

```sql
-- Connect to HIDS DB
psql -h localhost -p 5433 -U hids -d hids_alerts

-- Example alerts table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    source_ip VARCHAR(45),
    dest_ip VARCHAR(45),
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    description TEXT
);
```

## 🧪 Testing

```bash
# Test ML Service
curl http://localhost:5001/health

# Test Dashboard
curl http://localhost:5002/alerts

# Replay PCAP (if you have test.pcap)
docker exec hids_tcpreplay tcpreplay -i eth0 /pcaps/test.pcap
```
