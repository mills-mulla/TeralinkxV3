#!/bin/bash
# Train ML model on NSL-KDD dataset

echo "Training HIDS ML model on NSL-KDD dataset..."

docker exec hids_jupyter python3 << 'EOF'
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# Load NSL-KDD dataset
columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
           'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
           'num_compromised', 'root_shell', 'su_attempted', 'num_root', 'num_file_creations',
           'num_shells', 'num_access_files', 'num_outbound_cmds', 'is_host_login',
           'is_guest_login', 'count', 'srv_count', 'serror_rate', 'srv_serror_rate',
           'rerror_rate', 'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate',
           'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
           'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
           'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
           'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty']

print("Loading training data...")
train_df = pd.read_csv('/home/jovyan/datasets/KDDTrain+.txt', names=columns)

# Select 8 features matching HIDS engine
feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count',
                'serror_rate', 'srv_serror_rate', 'same_srv_rate']

# Use only NORMAL traffic for training (unsupervised learning)
X_train_normal = train_df[train_df['label'] == 'normal'][feature_cols]

print(f"Training on {len(X_train_normal)} normal samples...")

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train_normal)

# Train Isolation Forest
model = IsolationForest(
    contamination=0.1,  # Expect 10% anomalies
    random_state=42,
    n_estimators=100,
    max_samples='auto'
)
model.fit(X_scaled)

# Save model
import os
os.makedirs('/home/jovyan/models', exist_ok=True)
joblib.dump(model, '/home/jovyan/models/anomaly_detector.pkl')
joblib.dump(scaler, '/home/jovyan/models/scaler.pkl')

print("✅ Model trained and saved!")
print("Copying to ML service...")
EOF

# Copy trained model to ML service
docker cp hids_jupyter:/home/jovyan/models/anomaly_detector.pkl ./hids/models/
docker cp hids_jupyter:/home/jovyan/models/scaler.pkl ./hids/models/

# Restart ML service to load new model
docker compose restart ml_service

echo "✅ ML model updated! Restarting services..."
docker compose restart hids_engine

echo ""
echo "Model training complete!"
echo "Run: python3 hids/test_mvp.py to verify"
