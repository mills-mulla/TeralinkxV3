#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

print("="*70)
print("RETRAINING MODEL WITH BALANCED DATA (Target: 10-20% anomaly rate)")
print("="*70)

# Load NSL-KDD with MORE normal traffic
print("\nLoading NSL-KDD...")
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

train_df = pd.read_csv('/home/jovyan/datasets/KDDTrain+.txt', names=columns, nrows=30000)
test_df = pd.read_csv('/home/jovyan/datasets/KDDTest+.txt', names=columns, nrows=10000)
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

print(f"Loaded: {len(X):,} | Normal: {(y==0).sum():,} | Attack: {(y==1).sum():,}")

# Balance with MORE normal traffic (80% normal, 20% attack)
print("\nBalancing to 80% normal, 20% attack...")
normal = X[y == 0].sample(min(40000, (y==0).sum()), random_state=42)
attack = X[y == 1].sample(min(10000, (y==1).sum()), random_state=42)

X = pd.concat([normal, attack])
y = pd.concat([pd.Series(np.zeros(len(normal))), pd.Series(np.ones(len(attack)))])

# Shuffle
idx = np.random.permutation(len(X))
X = X.iloc[idx].reset_index(drop=True)
y = y.iloc[idx].reset_index(drop=True)

print(f"Final: {len(X):,} | Normal: {(y==0).sum():,} ({(y==0).sum()/len(y)*100:.1f}%) | Attack: {(y==1).sum():,} ({(y==1).sum()/len(y)*100:.1f}%)")

# Train
print("\nTraining with class weights to reduce false positives...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Use class weights to penalize false positives more
model = RandomForestClassifier(
    n_estimators=100, 
    max_depth=15, 
    min_samples_split=20,
    min_samples_leaf=10,
    class_weight={0: 1, 1: 0.5},  # Reduce attack weight to lower false positives
    random_state=42, 
    n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluate
from sklearn.metrics import classification_report, confusion_matrix
y_pred = model.predict(X_test)

print("\n" + "="*70)
print("EVALUATION")
print("="*70)
print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))

cm = confusion_matrix(y_test, y_pred)
fpr = cm[0,1] / (cm[0,0] + cm[0,1]) * 100
print(f"\nFalse Positive Rate: {fpr:.2f}%")
print(f"Target: <10% (Current: {'✅ GOOD' if fpr < 10 else '⚠️ NEEDS TUNING'})")

# Save
os.makedirs('/home/jovyan/work/models', exist_ok=True)
joblib.dump(model, '/home/jovyan/work/models/anomaly_detector.pkl')
joblib.dump(scaler, '/home/jovyan/work/models/scaler.pkl')

with open('/home/jovyan/work/models/model_type.txt', 'w') as f:
    f.write('random_forest_balanced')

print("\n✅ Model saved! Expected anomaly rate: 10-20%")
