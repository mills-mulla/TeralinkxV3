#!/usr/bin/env python3
"""
Memory-Efficient HIDS Training
Loads smaller samples to avoid memory issues
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("HIDS COMPREHENSIVE TRAINING (Memory Efficient)")
print("="*70)

# 1. Load NSL-KDD
print("\n[1/6] Loading NSL-KDD...")
columns = ['duration', 'protocol_type', 'service', 'flag', 'src_bytes', 
           'dst_bytes', 'land', 'wrong_fragment', 'urgent', 'hot', 
           'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
           'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
           'num_access_files', 'num_outbound_cmds', 'is_host_login',
           'is_guest_login', 'count', 'srv_count', 'serror_rate',
           'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
           'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
           'dst_host_srv_count', 'dst_host_same_srv_rate', 'dst_host_diff_srv_rate',
           'dst_host_same_src_port_rate', 'dst_host_srv_diff_host_rate',
           'dst_host_serror_rate', 'dst_host_srv_serror_rate',
           'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty']

train_df = pd.read_csv('/home/jovyan/datasets/KDDTrain+.txt', names=columns)
test_df = pd.read_csv('/home/jovyan/datasets/KDDTest+.txt', names=columns)
data = pd.concat([train_df, test_df], ignore_index=True)

X_nslkdd = pd.DataFrame({
    'src_port': 0,
    'dest_port': 0,
    'duration': data['duration'],
    'bytes_toserver': data['src_bytes'],
    'bytes_toclient': data['dst_bytes'],
    'pkts_toserver': data['count'],
    'proto': data['protocol_type'].map({'tcp': 1, 'udp': 2, 'icmp': 3}).fillna(1),
    'severity': 1
})
y_nslkdd = (data['label'] != 'normal').astype(int)

print(f"  ✓ Loaded: {len(X_nslkdd):,} samples")
print(f"    Normal: {(y_nslkdd==0).sum():,} ({(y_nslkdd==0).sum()/len(y_nslkdd)*100:.1f}%)")
print(f"    Attack: {(y_nslkdd==1).sum():,} ({(y_nslkdd==1).sum()/len(y_nslkdd)*100:.1f}%)")

del data, train_df, test_df

# 2. Load CICIDS2017 (small sample)
print("\n[2/6] Loading CICIDS2017...")
try:
    data = pd.read_csv('/home/jovyan/datasets/cicids2017_cleaned.csv', 
                       low_memory=False, nrows=50000)  # Only 50K rows
    data.columns = data.columns.str.strip()
    
    X_cicids17 = pd.DataFrame({
        'src_port': data.get('Source Port', 0),
        'dest_port': data.get('Destination Port', 0),
        'duration': data.get('Flow Duration', 0) / 1000000,
        'bytes_toserver': data.get('Total Length of Fwd Packets', 0),
        'bytes_toclient': data.get('Total Length of Bwd Packets', 0),
        'pkts_toserver': data.get('Total Fwd Packets', 1),
        'proto': 1,
        'severity': 1
    }).replace([np.inf, -np.inf], 0).fillna(0)
    
    label_col = [c for c in data.columns if 'label' in c.lower()][0]
    y_cicids17 = (data[label_col].str.strip().str.upper() != 'BENIGN').astype(int)
    
    print(f"  ✓ Loaded: {len(X_cicids17):,} samples")
    print(f"    Normal: {(y_cicids17==0).sum():,} ({(y_cicids17==0).sum()/len(y_cicids17)*100:.1f}%)")
    print(f"    Attack: {(y_cicids17==1).sum():,} ({(y_cicids17==1).sum()/len(y_cicids17)*100:.1f}%)")
    
    del data
except Exception as e:
    print(f"  ⚠️  Skipped: {e}")
    X_cicids17, y_cicids17 = None, None

# 3. Load CICIDS2018 (small sample)
print("\n[3/6] Loading CICIDS2018...")
try:
    data = pd.read_csv('/home/jovyan/datasets/Friday-02-03-2018_TrafficForML_CICFlowMeter.csv',
                       low_memory=False, nrows=30000)  # Only 30K rows
    
    X_cicids18 = pd.DataFrame({
        'src_port': data.get('Src Port', 0),
        'dest_port': data.get('Dst Port', 0),
        'duration': data.get('Flow Duration', 0) / 1000000,
        'bytes_toserver': data.get('Fwd Pkts Tot', 0) * 100,
        'bytes_toclient': data.get('Bwd Pkts Tot', 0) * 100,
        'pkts_toserver': data.get('Fwd Pkts Tot', 1),
        'proto': 1,
        'severity': 1
    }).replace([np.inf, -np.inf], 0).fillna(0)
    
    label_col = [c for c in data.columns if 'label' in c.lower()][0]
    y_cicids18 = (data[label_col].str.strip().str.upper() != 'BENIGN').astype(int)
    
    print(f"  ✓ Loaded: {len(X_cicids18):,} samples")
    print(f"    Normal: {(y_cicids18==0).sum():,} ({(y_cicids18==0).sum()/len(y_cicids18)*100:.1f}%)")
    print(f"    Attack: {(y_cicids18==1).sum():,} ({(y_cicids18==1).sum()/len(y_cicids18)*100:.1f}%)")
    
    del data
except Exception as e:
    print(f"  ⚠️  Skipped: {e}")
    X_cicids18, y_cicids18 = None, None

# 4. Combine datasets
print("\n[4/6] Combining and balancing datasets...")
X_all, y_all = [], []

for X, y in [(X_nslkdd, y_nslkdd), (X_cicids17, y_cicids17), (X_cicids18, y_cicids18)]:
    if X is not None:
        X_all.append(X)
        y_all.append(y)

X = pd.concat(X_all, ignore_index=True)
y = pd.concat(y_all, ignore_index=True)

print(f"  Combined: {len(X):,} samples")

# Balance to 50/50
normal = X[y == 0].sample(min(30000, (y==0).sum()), random_state=42)
attack = X[y == 1].sample(min(30000, (y==1).sum()), random_state=42)

X = pd.concat([normal, attack])
y = pd.concat([y[normal.index], y[attack.index]])

# Shuffle
idx = np.random.permutation(len(X))
X = X.iloc[idx].reset_index(drop=True)
y = y.iloc[idx].reset_index(drop=True)

print(f"  ✓ Balanced Dataset:")
print(f"    Normal: {(y==0).sum():,} ({(y==0).sum()/len(y)*100:.1f}%)")
print(f"    Attack: {(y==1).sum():,} ({(y==1).sum()/len(y)*100:.1f}%)")
print(f"    Total: {len(X):,} samples")

# 5. Train model
print("\n[5/6] Training Random Forest...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=20,
    min_samples_leaf=10,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
    verbose=2
)

print(f"  Training on {len(X_train):,} samples...")
model.fit(X_train_scaled, y_train)

# 6. Evaluate
print("\n[6/6] Evaluating model...")
y_pred = model.predict(X_test_scaled)

print("\n" + "="*70)
print("RESULTS")
print("="*70)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(f"  True Negatives:  {cm[0,0]:,}")
print(f"  False Positives: {cm[0,1]:,}")
print(f"  False Negatives: {cm[1,0]:,}")
print(f"  True Positives:  {cm[1,1]:,}")

fpr = cm[0,1] / (cm[0,0] + cm[0,1]) * 100
print(f"\n📊 False Positive Rate: {fpr:.2f}%")
print(f"   Status: {'✅ EXCELLENT' if fpr < 5 else '✅ GOOD' if fpr < 10 else '⚠️ NEEDS TUNING'}")

# Save model
print("\n" + "="*70)
print("SAVING MODEL")
print("="*70)
os.makedirs('/home/jovyan/work/models', exist_ok=True)

joblib.dump(model, '/home/jovyan/work/models/anomaly_detector.pkl')
joblib.dump(scaler, '/home/jovyan/work/models/scaler.pkl')
with open('/home/jovyan/work/models/model_type.txt', 'w') as f:
    f.write('random_forest_comprehensive')

print("✅ Model saved to /home/jovyan/work/models/")

print("\n" + "="*70)
print("✅ TRAINING COMPLETE!")
print("="*70)
print("\nNext: Deploy the model")
print("Run in terminal:")
print("  docker cp /home/jovyan/work/models/. hids_ml_service:/app/models/")
print("  docker restart hids_ml_service hids_engine")
