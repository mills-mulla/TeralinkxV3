# HIDS - Host Intrusion Detection System

## Quick Start

### Train Model
```bash
# Option 1: Python script (shows progress)
python3 train_comprehensive.py

# Option 2: Jupyter notebook (interactive)
# Open: notebooks/train_comprehensive.ipynb
```

### Deploy Model
```bash
docker cp models/. hids_ml_service:/app/models/
docker compose restart ml_service hids_engine
```

### Test
```bash
python3 test_mvp.py
```

### Generate Traffic
```bash
./generate_traffic.sh
```

## Structure

- `dashboard/` - Web dashboard
- `engine/` - Alert correlation engine
- `ml_service/` - ML anomaly detection
- `suricata/` - IDS rules and logs
- `zeek/` - Network monitoring
- `datasets/` - Training data (NSL-KDD, CICIDS)
- `models/` - Trained ML models
- `notebooks/` - Jupyter notebooks for training

## Training

Uses NSL-KDD + CICIDS2017 + CICIDS2018 datasets.
Balanced 50/50 (normal/attack) to reduce false positives.

Expected anomaly rate: 5-15%
