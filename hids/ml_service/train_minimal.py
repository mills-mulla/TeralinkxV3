#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

print("Loading NSL-KDD (minimal)...")
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

train_df = pd.read_csv('/home/jovyan/datasets/KDDTrain+.txt', names=columns).sample(20000)
test_df = pd.read_csv('/home/jovyan/datasets/KDDTest+.txt', names=columns).sample(5000)
data = pd.concat([train_df, test_df])

X = pd.DataFrame({
    'src_port': 0, 'dest_port': 0,
    'duration': data['duration'],
    'bytes_toserver': data['src_bytes'],
    'bytes_toclient': data['dst_bytes'],
    'pkts_toserver': data['count'],
    'proto': data['protocol_type'].map({'tcp': 1, 'udp': 2, 'icmp': 3}).fillna(1),
    'severity': 1
})
y = (data['label'] != 'normal').astype(int)

print(f"Loaded: {len(X):,} samples")
print(f"Normal: {(y==0).sum():,} | Attack: {(y==1).sum():,}")

print("\nBalancing...")
normal = X[y == 0].sample(min(10000, (y==0).sum()))
attack = X[y == 1].sample(min(10000, (y==1).sum()))
X = pd.concat([normal, attack])
y = pd.concat([y[normal.index], y[attack.index]])

print("\nTraining...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print(f"\nAccuracy: {score:.2%}")

os.makedirs('/home/jovyan/work/models', exist_ok=True)
joblib.dump(model, '/home/jovyan/work/models/anomaly_detector.pkl')
joblib.dump(scaler, '/home/jovyan/work/models/scaler.pkl')
print("\n✅ Model saved!")
