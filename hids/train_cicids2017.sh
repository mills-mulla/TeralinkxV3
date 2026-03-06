#!/bin/bash
# Download CIC-IDS2017 and Train Model

echo "=========================================="
echo "CIC-IDS2017 Download & Training"
echo "=========================================="
echo ""
echo "This will:"
echo "1. Download 2 CIC-IDS2017 files (~500MB each)"
echo "2. Train Random Forest model (~10 minutes)"
echo "3. Deploy to HIDS system"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

cd /home/ghost/Desktop/TeralinkxV3/hids/datasets

echo ""
echo "Step 1: Downloading CIC-IDS2017 files..."
echo "This may take 10-20 minutes depending on your connection."
echo ""

# Download DDoS file (~500MB)
if [ ! -s "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" ]; then
    echo "Downloading DDoS dataset..."
    wget -O Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv \
        "https://iscxdownloads.cs.unb.ca/iscxdownloads/CIC-IDS-2017/Dataset/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" \
        || echo "Download failed. Try manual download from: https://www.unb.ca/cic/datasets/ids-2017.html"
else
    echo "✅ DDoS file already exists"
fi

# Download PortScan file (~300MB)
if [ ! -s "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv" ]; then
    echo "Downloading PortScan dataset..."
    wget -O Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv \
        "https://iscxdownloads.cs.unb.ca/iscxdownloads/CIC-IDS-2017/Dataset/MachineLearningCSV/MachineLearningCVE/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv" \
        || echo "Download failed. Try manual download from: https://www.unb.ca/cic/datasets/ids-2017.html"
else
    echo "✅ PortScan file already exists"
fi

echo ""
echo "Step 2: Copying files to Jupyter container..."
docker cp Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv hids_jupyter:/home/jovyan/datasets/ 2>/dev/null
docker cp Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv hids_jupyter:/home/jovyan/datasets/ 2>/dev/null

echo ""
echo "Step 3: Training model on CIC-IDS2017..."
echo "This will take 10-15 minutes..."

docker exec hids_jupyter python3 << 'PYTHON_EOF'
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

print("Loading CIC-IDS2017 datasets...")

try:
    df1 = pd.read_csv('/home/jovyan/datasets/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv', encoding='latin1')
    print(f"✅ Loaded DDoS: {len(df1)} samples")
except Exception as e:
    print(f"❌ Failed to load DDoS file: {e}")
    exit(1)

try:
    df2 = pd.read_csv('/home/jovyan/datasets/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv', encoding='latin1')
    print(f"✅ Loaded PortScan: {len(df2)} samples")
except Exception as e:
    print(f"❌ Failed to load PortScan file: {e}")
    exit(1)

# Combine datasets
data = pd.concat([df1, df2], ignore_index=True)
print(f"\nTotal samples: {len(data)}")

# Clean column names
data.columns = data.columns.str.strip()

# Map CIC-IDS2017 features to HIDS 8 features
print("\nMapping features...")
feature_mapping = {
    'Flow Duration': 'duration',
    'Total Fwd Packets': 'src_bytes',
    'Total Backward Packets': 'dst_bytes',
    'Flow Packets/s': 'count',
    'Flow Bytes/s': 'srv_count',
    'Fwd PSH Flags': 'serror_rate',
    'Bwd PSH Flags': 'srv_serror_rate',
    'Idle Mean': 'same_srv_rate'
}

X = data[list(feature_mapping.keys())].copy()
X.columns = list(feature_mapping.values())

# Handle missing/infinite values
X = X.fillna(0)
X = X.replace([np.inf, -np.inf], 0)

# Binary labels (BENIGN vs Attack)
y = (data['Label'] != 'BENIGN').astype(int)

print(f"Normal samples: {(y==0).sum()}")
print(f"Attack samples: {(y==1).sum()}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples")

# Scale features
print("\nScaling features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train Random Forest
print("\nTraining Random Forest Classifier...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_split=10,
    min_samples_leaf=4,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
    verbose=1
)

model.fit(X_train_scaled, y_train)

# Evaluate
print("\nEvaluating model...")
y_pred = model.predict(X_test_scaled)

print("\n" + "="*70)
print("RESULTS")
print("="*70)
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

# Feature importance
print("\nFeature Importance:")
for feat, imp in zip(X.columns, model.feature_importances_):
    print(f"  {feat:20s}: {imp:.4f}")

# Save model
print("\nSaving model...")
os.makedirs('/home/jovyan/models', exist_ok=True)
joblib.dump(model, '/home/jovyan/models/anomaly_detector.pkl')
joblib.dump(scaler, '/home/jovyan/models/scaler.pkl')

with open('/home/jovyan/models/model_type.txt', 'w') as f:
    f.write('random_forest_supervised_cicids2017')

print("\n✅ Model trained on CIC-IDS2017 and saved!")
PYTHON_EOF

echo ""
echo "Step 4: Deploying model to HIDS..."
cd /home/ghost/Desktop/TeralinkxV3
docker cp hids_jupyter:/home/jovyan/models/anomaly_detector.pkl ./hids/models/
docker cp hids_jupyter:/home/jovyan/models/scaler.pkl ./hids/models/
docker cp hids_jupyter:/home/jovyan/models/model_type.txt ./hids/models/

docker compose restart ml_service hids_engine

echo ""
echo "Step 5: Waiting for services to start..."
sleep 15

echo ""
echo "=========================================="
echo "✅ Training Complete!"
echo "=========================================="
echo ""
echo "Testing the new model..."
python3 hids/test_mvp.py

echo ""
echo "Model trained on CIC-IDS2017 dataset!"
echo "Access dashboard: http://localhost:5002"
