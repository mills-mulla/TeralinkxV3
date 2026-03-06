#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

print("="*70)
print("Training HIDS ML Model with CIC-IDS2017")
print("="*70)

# Load dataset
print("\nLoading dataset...")
df = pd.read_csv('/app/cicids2017_cleaned.csv')
print(f"✅ Loaded {len(df):,} samples")
print(f"   Columns: {len(df.columns)}")

# Clean column names
df.columns = df.columns.str.strip()
print(f"\nColumns: {list(df.columns[:10])}...")

# Map to 8 features
feature_map = {
    'Source Port': 'src_port',
    'Destination Port': 'dest_port', 
    'Flow Duration': 'duration',
    'Total Fwd Packets': 'bytes_toserver',
    'Total Backward Packets': 'bytes_toclient',
    'Flow Packets/s': 'pkts_toserver',
    'Protocol': 'proto',
    'Flow Bytes/s': 'severity'
}

# Extract features
X = pd.DataFrame()
for cic_col, hids_col in feature_map.items():
    if cic_col in df.columns:
        X[hids_col] = df[cic_col]
        print(f"✅ {cic_col} → {hids_col}")

# Fill missing
for col in ['src_port', 'dest_port', 'duration', 'bytes_toserver', 'bytes_toclient', 'pkts_toserver', 'proto', 'severity']:
    if col not in X.columns:
        X[col] = 0

X = X.replace([np.inf, -np.inf], 0).fillna(0)

# Labels
label_col = [c for c in df.columns if 'label' in c.lower()][0]
y = (df[label_col].str.strip().str.upper() != 'BENIGN').astype(int)

print(f"\n✅ Features: {X.shape}")
print(f"   Normal: {(y==0).sum():,}, Attack: {(y==1).sum():,}")

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Scale
print("\nScaling...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train
print("\nTraining Random Forest (this takes 10-15 min)...")
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
print("\n" + "="*70)
print("Evaluation")
print("="*70)
y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

# Save
print("\nSaving model...")
os.makedirs('/app/models', exist_ok=True)
joblib.dump(model, '/app/models/anomaly_detector.pkl')
joblib.dump(scaler, '/app/models/scaler.pkl')
with open('/app/models/model_type.txt', 'w') as f:
    f.write('random_forest_supervised')

print("\n✅ Training complete!")
print("Model saved to /app/models/")
