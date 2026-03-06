#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import glob

print("="*70)
print("COMPREHENSIVE TRAINING: NSL-KDD + CICIDS2017 + CICIDS2018")
print("="*70)

# ============ NSL-KDD ============
print("\n[1/3] Loading NSL-KDD...")
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

train_df = pd.read_csv('/home/jovyan/datasets/KDDTrain+.txt', names=columns, nrows=15000)
test_df = pd.read_csv('/home/jovyan/datasets/KDDTest+.txt', names=columns, nrows=5000)
data = pd.concat([train_df, test_df])

X_nslkdd = pd.DataFrame({
    'src_port': 0, 'dest_port': 0,
    'duration': data['duration'],
    'bytes_toserver': data['src_bytes'],
    'bytes_toclient': data['dst_bytes'],
    'pkts_toserver': data['count'],
    'proto': data['protocol_type'].map({'tcp': 1, 'udp': 2, 'icmp': 3}).fillna(1),
    'severity': 1
})
y_nslkdd = (data['label'] != 'normal').astype(int)
print(f"  Loaded: {len(X_nslkdd):,} | Normal: {(y_nslkdd==0).sum():,} | Attack: {(y_nslkdd==1).sum():,}")

# ============ CICIDS2017 ============
print("\n[2/3] Loading CICIDS2017...")
if os.path.exists('/home/jovyan/datasets/cicids2017_cleaned.csv'):
    data = pd.read_csv('/home/jovyan/datasets/cicids2017_cleaned.csv', low_memory=False, nrows=15000)
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
    
    label_col = 'Attack Type' if 'Attack Type' in data.columns else [c for c in data.columns if 'label' in c.lower()][0]
    # CICIDS2017 uses 'Normal Traffic' as the normal label
    y_cicids17 = (data[label_col].str.strip() != 'Normal Traffic').astype(int)
    print(f"  Loaded: {len(X_cicids17):,} | Normal: {(y_cicids17==0).sum():,} | Attack: {(y_cicids17==1).sum():,}")
else:
    X_cicids17, y_cicids17 = None, None
    print("  ⚠️  CICIDS2017 not found, skipping")

# ============ CICIDS2018 ============
print("\n[3/3] Loading CICIDS2018...")
csv_files = glob.glob('/home/jovyan/datasets/*2018*.csv')
if csv_files:
    dfs = []
    for file in csv_files[:2]:
        try:
            df = pd.read_csv(file, low_memory=False, nrows=7500)
            dfs.append(df)
        except:
            pass
    
    if dfs:
        data = pd.concat(dfs, ignore_index=True)
        
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
        
        label_col = 'Label' if 'Label' in data.columns else [c for c in data.columns if 'label' in c.lower()][0]
        # CICIDS2018 uses 'Benign' as the normal label
        y_cicids18 = (data[label_col].str.strip() != 'Benign').astype(int)
        print(f"  Loaded: {len(X_cicids18):,} | Normal: {(y_cicids18==0).sum():,} | Attack: {(y_cicids18==1).sum():,}")
    else:
        X_cicids18, y_cicids18 = None, None
        print("  ⚠️  CICIDS2018 files unreadable, skipping")
else:
    X_cicids18, y_cicids18 = None, None
    print("  ⚠️  CICIDS2018 not found, skipping")

# ============ COMBINE ============
print("\n" + "="*70)
print("COMBINING DATASETS")
print("="*70)

X_all, y_all = [X_nslkdd], [y_nslkdd]
if X_cicids17 is not None:
    X_all.append(X_cicids17)
    y_all.append(y_cicids17)
if X_cicids18 is not None:
    X_all.append(X_cicids18)
    y_all.append(y_cicids18)

X = pd.concat(X_all, ignore_index=True)
y = pd.concat(y_all, ignore_index=True)

print(f"Combined: {len(X):,} | Normal: {(y==0).sum():,} | Attack: {(y==1).sum():,}")

# Balance
print("\nBalancing to 50/50...")
normal = X[y == 0].sample(min(15000, (y==0).sum()), random_state=42)
attack = X[y == 1].sample(min(15000, (y==1).sum()), random_state=42)
X = pd.concat([normal, attack])
y = pd.concat([pd.Series(np.zeros(len(normal))), pd.Series(np.ones(len(attack)))])

# Shuffle
idx = np.random.permutation(len(X))
X = X.iloc[idx].reset_index(drop=True)
y = y.iloc[idx].reset_index(drop=True)

print(f"Final: {len(X):,} | Normal: {(y==0).sum():,} ({(y==0).sum()/len(y)*100:.1f}%) | Attack: {(y==1).sum():,} ({(y==1).sum()/len(y)*100:.1f}%)")

# ============ TRAIN ============
print("\n" + "="*70)
print("TRAINING RANDOM FOREST")
print("="*70)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Train: {len(X_train):,} | Test: {len(X_test):,}")

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=100, max_depth=15, min_samples_split=20, 
                                min_samples_leaf=10, random_state=42, n_jobs=-1, verbose=1)
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print(f"\n✅ Test Accuracy: {score:.2%}")

# ============ SAVE ============
os.makedirs('/home/jovyan/work/models', exist_ok=True)
joblib.dump(model, '/home/jovyan/work/models/anomaly_detector.pkl')
joblib.dump(scaler, '/home/jovyan/work/models/scaler.pkl')

with open('/home/jovyan/work/models/model_type.txt', 'w') as f:
    f.write('random_forest_comprehensive')

print("\n" + "="*70)
print("✅ MODEL SAVED TO /home/jovyan/work/models/")
print("="*70)
