# HIDS Stack Deployment Guide

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HIDS STACK                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Network Traffic                                        │
│       ↓                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │ Suricata │  │   Zeek   │  │TCPReplay │            │
│  │  (IDS)   │  │  (Flow)  │  │ (Replay) │            │
│  └────┬─────┘  └────┬─────┘  └──────────┘            │
│       │             │                                   │
│       └─────┬───────┘                                   │
│             ↓                                           │
│      ┌─────────────┐                                   │
│      │ HIDS Engine │                                   │
│      │  (Correlate)│                                   │
│      └──────┬──────┘                                   │
│             │                                           │
│       ┌─────┴─────┐                                    │
│       ↓           ↓                                    │
│  ┌────────┐  ┌──────────┐                            │
│  │ Redis  │  │PostgreSQL│                            │
│  │(Buffer)│  │ (Alerts) │                            │
│  └────────┘  └─────┬────┘                            │
│                    │                                   │
│              ┌─────┴─────┐                            │
│              ↓           ↓                            │
│         ┌─────────┐ ┌──────────┐                     │
│         │Dashboard│ │ML Service│                     │
│         │ :5002   │ │  :5001   │                     │
│         └─────────┘ └──────────┘                     │
│                          ↑                            │
│                     ┌────┴────┐                       │
│                     │ Jupyter │                       │
│                     │  :8888  │                       │
│                     └─────────┘                       │
└─────────────────────────────────────────────────────────┘
```

## Services

### 1. Suricata (Signature IDS)
- **Image**: jasonish/suricata
- **Mode**: host network (requires NET_ADMIN)
- **Logs**: `./hids/suricata/logs/`
- **Rules**: `./hids/suricata/rules/`

### 2. Zeek (Flow Analysis)
- **Image**: zeekurity/zeek
- **Mode**: host network (requires NET_ADMIN)
- **Logs**: `./hids/zeek/logs/`
- **Scripts**: `./hids/zeek/scripts/`

### 3. TCPReplay (Packet Replay)
- **Image**: networkstatic/tcpreplay
- **Mode**: host network
- **PCAPs**: `./hids/pcaps/`

### 4. Redis (Correlation Buffer)
- **Reuses existing Redis service**
- Port: 6379

### 5. Jupyter (ML Training)
- **Image**: jupyter/scipy-notebook
- **Port**: 8888
- **Notebooks**: `./hids/notebooks/`
- **Datasets**: `./hids/datasets/`

### 6. ML Service (Flask + scikit-learn)
- **Port**: 5001
- **Endpoint**: `/predict`
- **Models**: `./hids/models/`

### 7. HIDS Engine (Python + pandas)
- Processes Suricata & Zeek logs
- Correlates events
- Stores alerts in PostgreSQL

### 8. Dashboard (Flask)
- **Port**: 5002
- **Endpoint**: `/alerts`

### 9. HIDS Database (PostgreSQL)
- **Port**: 5433
- **Database**: hids_alerts
- **User**: hids

## Deployment

```bash
cd /home/ghost/Desktop/TeralinkxV3

# Start HIDS stack
docker-compose up -d suricata zeek hids_db hids_engine hids_dashboard ml_service jupyter

# View logs
docker-compose logs -f hids_engine

# Access Jupyter
# http://localhost:8888

# Access Dashboard
# http://localhost:5002

# Access ML Service
# http://localhost:5001/health
```

## Network Interface

Update `suricata.yaml` and Zeek config to match your network interface:
- Default: `eth0`
- Check with: `ip link show`

## Next Steps

1. Configure Suricata rules in `./hids/suricata/rules/`
2. Add Zeek scripts in `./hids/zeek/scripts/`
3. Train ML models in Jupyter
4. Implement HIDS Engine correlation logic
5. Build Dashboard UI
