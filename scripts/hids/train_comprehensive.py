#!/usr/bin/env python3
"""
Comprehensive HIDS Training
Uses: CICIDS2017, CICIDS2018, NSL-KDD, UNSW-NB15
Includes rich normal traffic baseline
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import glob

def load_nslkdd(dataset_path='./datasets'):
    """Load NSL-KDD dataset (excellent normal traffic baseline)"""
    print("\n" + "=" * 70)
    print("Loading NSL-KDD Dataset")
    print("=" * 70)
    
    train_file = f'{dataset_path}/KDDTrain+.txt'
    test_file = f'{dataset_path}/KDDTest+.txt'
    
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
    
    dfs = []
    for file in [train_file, test_file]:
        if os.path.exists(file):
            df = pd.read_csv(file, names=columns)
            dfs.append(df)
            print(f"✓ Loaded {os.path.basename(file)}: {len(df):,} samples")
    
    if dfs:
        data = pd.concat(dfs, ignore_index=True)
        
        # Map to HIDS features
        X = pd.DataFrame({
            'src_port': 0,
            'dest_port': 0,
            'duration': data['duration'],
            'bytes_toserver': data['src_bytes'],
            'bytes_toclient': data['dst_bytes'],
            'pkts_toserver': data['count'],
            'proto': data['protocol_type'].map({'tcp': 1, 'udp': 2, 'icmp': 3}).fillna(1),
            'severity': 1
        })
        
        y = (data['label'] != 'normal').astype(int)
        
        print(f"\n✅ NSL-KDD Total: {len(X):,}")
        print(f"   Normal: {(y==0).sum():,} ({(y==0).sum()/len(y)*100:.1f}%)")
        print(f"   Attack: {(y==1).sum():,} ({(y==1).sum()/len(y)*100:.1f}%)")
        
        return X, y
    
    return None, None

def load_cicids2017(dataset_path='./datasets'):
    """Load CICIDS2017"""
    print("\n" + "=" * 70)
    print("Loading CICIDS2017 Dataset")
    print("=" * 70)
    
    csv_files = glob.glob(f'{dataset_path}/*ISCX.csv')
    
    if not csv_files:
        print("⚠️  CICIDS2017 not found")
        return None, None
    
    dfs = []
    for file in csv_files[:5]:
        try:
            df = pd.read_csv(file, encoding='latin1', low_memory=False)
            df.columns = df.columns.str.strip()
            dfs.append(df)
            print(f"✓ {os.path.basename(file)}: {len(df):,}")
        except:
            pass
    
    if dfs:
        data = pd.concat(dfs, ignore_index=True).sample(100000, random_state=42) if len(pd.concat(dfs)) > 100000 else pd.concat(dfs, ignore_index=True)
        
        X = pd.DataFrame({
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
        y = (data[label_col].str.strip().str.upper() != 'BENIGN').astype(int)
        
        print(f"\n✅ CICIDS2017 Total: {len(X):,}")
        print(f"   Normal: {(y==0).sum():,} ({(y==0).sum()/len(y)*100:.1f}%)")
        print(f"   Attack: {(y==1).sum():,} ({(y==1).sum()/len(y)*100:.1f}%)")
        
        return X, y
    
    return None, None

def load_cicids2018(dataset_path='./datasets'):
    """Load CICIDS2018"""
    print("\n" + "=" * 70)
    print("Loading CICIDS2018 Dataset")
    print("=" * 70)
    
    csv_files = glob.glob(f'{dataset_path}/*2018*.csv')
    
    if not csv_files:
        print("⚠️  CICIDS2018 not found")
        return None, None
    
    dfs = []
    for file in csv_files[:3]:
        try:
            df = pd.read_csv(file, low_memory=False)
            dfs.append(df)
            print(f"✓ {os.path.basename(file)}: {len(df):,}")
        except:
            pass
    
    if dfs:
        data = pd.concat(dfs, ignore_index=True).sample(50000, random_state=42) if len(pd.concat(dfs)) > 50000 else pd.concat(dfs, ignore_index=True)
        
        X = pd.DataFrame({
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
        y = (data[label_col].str.strip().str.upper() != 'BENIGN').astype(int)
        
        print(f"\n✅ CICIDS2018 Total: {len(X):,}")
        print(f"   Normal: {(y==0).sum():,} ({(y==0).sum()/len(y)*100:.1f}%)")
        print(f"   Attack: {(y==1).sum():,} ({(y==1).sum()/len(y)*100:.1f}%)")
        
        return X, y
    
    return None, None

def train_comprehensive_model(datasets):
    """Train on combined datasets"""
    print("\n" + "=" * 70)
    print("Training Comprehensive Model")
    print("=" * 70)
    
    X_all, y_all = [], []
    
    for X, y in datasets:
        if X is not None:
            X_all.append(X)
            y_all.append(y)
    
    X = pd.concat(X_all, ignore_index=True)
    y = pd.concat(y_all, ignore_index=True)
    
    # Balance dataset
    normal = X[y == 0].sample(min(50000, (y==0).sum()), random_state=42)
    attack = X[y == 1].sample(min(50000, (y==1).sum()), random_state=42)
    
    X = pd.concat([normal, attack])
    y = pd.concat([y[normal.index], y[attack.index]])
    
    # Shuffle
    idx = np.random.permutation(len(X))
    X, y = X.iloc[idx].reset_index(drop=True), y.iloc[idx].reset_index(drop=True)
    
    print(f"\nFinal Balanced Dataset:")
    print(f"  Normal: {(y==0).sum():,}")
    print(f"  Attack: {(y==1).sum():,}")
    print(f"  Total: {len(X):,}")
    print(f"  Balance: {(y==0).sum()/len(y)*100:.1f}% / {(y==1).sum()/len(y)*100:.1f}%")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("\nTraining Random Forest...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=20,
        min_samples_leaf=10,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    
    print("\n" + "=" * 70)
    print("Model Evaluation")
    print("=" * 70)
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
    
    return model, scaler

def save_model(model, scaler):
    os.makedirs('./models', exist_ok=True)
    joblib.dump(model, './models/anomaly_detector.pkl')
    joblib.dump(scaler, './models/scaler.pkl')
    with open('./models/model_type.txt', 'w') as f:
        f.write('random_forest_comprehensive')
    print("\n✅ Model saved to ./models/")

def main():
    print("=" * 70)
    print("COMPREHENSIVE HIDS TRAINING")
    print("Using: NSL-KDD + CICIDS2017 + CICIDS2018")
    print("=" * 70)
    
    datasets = [
        load_nslkdd(),
        load_cicids2017(),
        load_cicids2018()
    ]
    
    datasets = [d for d in datasets if d[0] is not None]
    
    if not datasets:
        print("\n❌ No datasets found. Run: ./download_datasets.sh")
        return
    
    model, scaler = train_comprehensive_model(datasets)
    save_model(model, scaler)
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print("\nDeploy: docker cp ./models/. hids_ml_service:/app/models/")
    print("Restart: docker compose restart ml_service hids_engine")

if __name__ == '__main__':
    main()
