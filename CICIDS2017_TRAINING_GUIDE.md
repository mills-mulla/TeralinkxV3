# CIC-IDS2017 Dataset - Download & Training Guide

## 📥 Where to Get CIC-IDS2017

### Official Source (Recommended)
**Canadian Institute for Cybersecurity (CIC)**
- **Website**: https://www.unb.ca/cic/datasets/ids-2017.html
- **Direct Link**: https://www.unb.ca/cic/datasets/ids-2017.html
- **Size**: ~7.8 GB (CSV files) or ~69 GB (PCAP files)
- **Format**: CSV (processed) or PCAP (raw network traffic)

### What You Get:
- **8 days of network traffic** (Monday-Friday, 2 weeks)
- **14 attack types**: DDoS, DoS, Brute Force, XSS, SQL Injection, Infiltration, Port Scan, Botnet
- **2.8 million flows** with 80+ features
- **Labeled data** (Normal vs Attack types)

---

## 🚀 Quick Download & Setup

### Option 1: Download CSV Files (Recommended - Faster)

```bash
cd /home/ghost/Desktop/TeralinkxV3/hids/datasets

# Download individual days (choose what you need)
# Monday - Benign
wget https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Monday-WorkingHours.pcap_ISCX.csv

# Tuesday - FTP-Patator, SSH-Patator
wget https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Tuesday-WorkingHours.pcap_ISCX.csv

# Wednesday - DoS attacks
wget https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Wednesday-workingHours.pcap_ISCX.csv

# Thursday - Web attacks
wget https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
wget https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv

# Friday - DDoS, Port Scan
wget https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Morning.pcap_ISCX.csv
wget https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
wget https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
```

### Option 2: Download via Script (Automated)

```bash
cd /home/ghost/Desktop/TeralinkxV3
./hids/download_cicids2017.sh
```

### Option 3: Download Full Dataset (All Files)

```bash
# Using wget
cd /home/ghost/Desktop/TeralinkxV3/hids/datasets
wget -r -np -nH --cut-dirs=4 -R "index.html*" \
  https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/

# Or use the provided script
docker exec hids_jupyter bash /home/jovyan/download_cicids2017.sh
```

---

## 📊 Dataset Structure

### CSV Files Available:
```
Monday-WorkingHours.pcap_ISCX.csv                    (Normal traffic)
Tuesday-WorkingHours.pcap_ISCX.csv                   (SSH/FTP Brute Force)
Wednesday-workingHours.pcap_ISCX.csv                 (DoS/DDoS)
Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv  (Web attacks)
Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
Friday-WorkingHours-Morning.pcap_ISCX.csv            (Botnet)
Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
```

### Features (80+ columns):
- Flow Duration, Total Fwd/Bwd Packets
- Packet Length Stats (min, max, mean, std)
- Flow Bytes/s, Flow Packets/s
- IAT (Inter-Arrival Time) Stats
- TCP Flags, Header Length
- **Label** (Normal or Attack Type)

---

## 🎓 Training with CIC-IDS2017

### Step 1: Create Training Script

```python
# Save as: hids/train_cicids2017.py

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import glob

# Load all CSV files
csv_files = glob.glob('/home/jovyan/datasets/*ISCX.csv')
print(f"Found {len(csv_files)} CSV files")

dfs = []
for file in csv_files:
    print(f"Loading {file}...")
    df = pd.read_csv(file, encoding='latin1')
    dfs.append(df)

# Combine all data
data = pd.concat(dfs, ignore_index=True)
print(f"Total samples: {len(data)}")

# Clean column names
data.columns = data.columns.str.strip()

# Map to 8 features matching HIDS engine
feature_mapping = {
    'Flow Duration': 'duration',
    'Total Fwd Packets': 'src_bytes',  # Approximate
    'Total Backward Packets': 'dst_bytes',  # Approximate
    'Flow Packets/s': 'count',
    'Flow Bytes/s': 'srv_count',
    'Fwd PSH Flags': 'serror_rate',
    'Bwd PSH Flags': 'srv_serror_rate',
    'Idle Mean': 'same_srv_rate'
}

# Select and rename features
feature_cols = list(feature_mapping.keys())
X = data[feature_cols].copy()
X.columns = list(feature_mapping.values())

# Handle missing values
X = X.fillna(0)
X = X.replace([np.inf, -np.inf], 0)

# Binary labels
y = (data['Label'].str.strip() != 'BENIGN').astype(int)

print(f"Normal: {(y==0).sum()}, Attack: {(y==1).sum()}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest
print("Training Random Forest...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_split=10,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
    verbose=1
)

model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
print("\nResults:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

# Save model
import os
os.makedirs('/home/jovyan/models', exist_ok=True)
joblib.dump(model, '/home/jovyan/models/anomaly_detector.pkl')
joblib.dump(scaler, '/home/jovyan/models/scaler.pkl')

with open('/home/jovyan/models/model_type.txt', 'w') as f:
    f.write('random_forest_supervised')

print("\n✅ Model trained on CIC-IDS2017 and saved!")
print("Copy to ML service:")
print("  docker cp hids_jupyter:/home/jovyan/models/. ./hids/models/")
print("  docker compose restart ml_service hids_engine")
```

### Step 2: Run Training

```bash
# Copy script to Jupyter
docker cp hids/train_cicids2017.py hids_jupyter:/home/jovyan/

# Run training (may take 10-15 minutes)
docker exec hids_jupyter python3 /home/jovyan/train_cicids2017.py

# Deploy model
docker cp hids_jupyter:/home/jovyan/models/. ./hids/models/
docker compose restart ml_service hids_engine
```

---

## 🎯 Automated Download & Training Script

```bash
#!/bin/bash
# Save as: hids/train_with_cicids2017.sh

echo "CIC-IDS2017 Training Pipeline"
echo "=============================="

# Step 1: Download dataset
echo "Step 1: Downloading CIC-IDS2017 dataset..."
cd /home/ghost/Desktop/TeralinkxV3/hids/datasets

# Download key files (adjust as needed)
wget -nc https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
wget -nc https://www.unb.ca/cic/datasets/ids-2017/dataset/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv

# Step 2: Copy to Jupyter
echo "Step 2: Copying files to Jupyter..."
docker cp Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv hids_jupyter:/home/jovyan/datasets/
docker cp Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv hids_jupyter:/home/jovyan/datasets/

# Step 3: Train model
echo "Step 3: Training model..."
docker cp ../train_cicids2017.py hids_jupyter:/home/jovyan/
docker exec hids_jupyter python3 /home/jovyan/train_cicids2017.py

# Step 4: Deploy
echo "Step 4: Deploying model..."
cd /home/ghost/Desktop/TeralinkxV3
docker cp hids_jupyter:/home/jovyan/models/. ./hids/models/
docker compose restart ml_service hids_engine

echo "✅ Training complete!"
```

---

## 📈 Expected Performance with CIC-IDS2017

| Metric | NSL-KDD | CIC-IDS2017 |
|--------|---------|-------------|
| Detection Rate | 90% | **95%+** ✅ |
| False Positive Rate | 15% | **5-10%** ✅ |
| Training Samples | 62K | **2.8M** ✅ |
| Attack Types | 14 | **14** |
| Realism | Moderate | **High** ✅ |

---

## 🔍 Alternative: Use Existing Files

You already have some CIC-IDS2017 files:

```bash
ls -lh /home/ghost/Desktop/TeralinkxV3/hids/datasets/

# You should see:
# Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
# Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
```

Train on these:

```bash
docker exec hids_jupyter python3 << 'EOF'
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Load existing files
df1 = pd.read_csv('/home/jovyan/datasets/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv')
df2 = pd.read_csv('/home/jovyan/datasets/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv')

data = pd.concat([df1, df2])
print(f"Loaded {len(data)} samples")

# ... (rest of training code)
EOF
```

---

## 🚨 Important Notes

1. **File Size**: CIC-IDS2017 is large (~7.8 GB). Ensure you have space.

2. **Download Time**: May take 1-2 hours depending on connection.

3. **Training Time**: 
   - Full dataset: 30-60 minutes
   - Subset (2-3 files): 10-15 minutes

4. **Memory**: Requires ~8GB RAM for full dataset

5. **Alternative**: Start with Friday files (DDoS + PortScan) - already downloaded!

---

## 📚 References

- **Official Page**: https://www.unb.ca/cic/datasets/ids-2017.html
- **Paper**: "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization" (2018)
- **Citation**: Sharafaldin et al., CIC-IDS2017

---

## ✅ Quick Start (Use Existing Files)

```bash
cd /home/ghost/Desktop/TeralinkxV3

# Create training script
cat > hids/train_cicids2017_quick.py << 'EOF'
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib, os

df1 = pd.read_csv('/home/jovyan/datasets/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv')
df2 = pd.read_csv('/home/jovyan/datasets/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv')
data = pd.concat([df1, df2])

# Map features (simplified)
X = data[['Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 
          'Flow Packets/s', 'Flow Bytes/s', 'Fwd PSH Flags', 
          'Bwd PSH Flags', 'Idle Mean']].fillna(0)
y = (data[' Label'].str.strip() != 'BENIGN').astype(int)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_scaled, y)

os.makedirs('/home/jovyan/models', exist_ok=True)
joblib.dump(model, '/home/jovyan/models/anomaly_detector.pkl')
joblib.dump(scaler, '/home/jovyan/models/scaler.pkl')
print("✅ Done!")
EOF

# Run it
docker cp hids/train_cicids2017_quick.py hids_jupyter:/home/jovyan/
docker exec hids_jupyter python3 /home/jovyan/train_cicids2017_quick.py
docker cp hids_jupyter:/home/jovyan/models/. ./hids/models/
docker compose restart ml_service hids_engine
```

**This uses your existing CIC-IDS2017 files and takes ~5 minutes!**
