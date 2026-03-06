#!/usr/bin/env python3
"""
CIC-IDS2017 Training Script for HIDS ML Model
Trains Random Forest on CIC-IDS2017 dataset with proper feature mapping
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import glob

def load_cicids2017_data(dataset_path='/home/jovyan/datasets'):
    """Load and combine all CIC-IDS2017 CSV files"""
    print("=" * 70)
    print("Loading CIC-IDS2017 Dataset")
    print("=" * 70)
    
    csv_files = glob.glob(f'{dataset_path}/*ISCX.csv')
    
    if not csv_files:
        print(f"❌ No CIC-IDS2017 CSV files found in {dataset_path}")
        print("\nExpected files like:")
        print("  - Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv")
        print("  - Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv")
        return None
    
    print(f"Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"  - {os.path.basename(f)}")
    
    dfs = []
    for file in csv_files:
        try:
            print(f"\nLoading {os.path.basename(file)}...")
            df = pd.read_csv(file, encoding='latin1', low_memory=False)
            print(f"  Loaded {len(df):,} samples")
            dfs.append(df)
        except Exception as e:
            print(f"  ⚠️  Error loading {file}: {e}")
    
    if not dfs:
        return None
    
    data = pd.concat(dfs, ignore_index=True)
    print(f"\n✅ Total samples loaded: {len(data):,}")
    
    return data

def map_features_to_hids(data):
    """Map CIC-IDS2017 features to HIDS 8-feature model
    
    HIDS expects 8 features:
    1. src_port (Source Port)
    2. dest_port (Destination Port)
    3. duration (Flow Duration)
    4. bytes_toserver (Bytes sent to server)
    5. bytes_toclient (Bytes sent to client)
    6. pkts_toserver (Packets sent to server)
    7. proto (Protocol: 1=TCP, 2=UDP, 3=ICMP)
    8. severity (Alert severity, default=1 for ML)
    """
    print("\n" + "=" * 70)
    print("Feature Mapping: CIC-IDS2017 → HIDS 8-Feature Model")
    print("=" * 70)
    
    # Clean column names
    data.columns = data.columns.str.strip()
    
    # CIC-IDS2017 → HIDS feature mapping
    feature_mapping = {
        'Source Port': 'src_port',
        'Destination Port': 'dest_port',
        'Flow Duration': 'duration',
        'Total Fwd Packets': 'bytes_toserver',      # Approximate
        'Total Backward Packets': 'bytes_toclient',  # Approximate
        'Flow Packets/s': 'pkts_toserver',           # Approximate
        'Protocol': 'proto',
        'Flow Bytes/s': 'severity'                   # Use as proxy
    }
    
    # Check which features exist
    available_features = {}
    for cic_col, hids_col in feature_mapping.items():
        if cic_col in data.columns:
            available_features[cic_col] = hids_col
            print(f"✅ {cic_col:30s} → {hids_col}")
        else:
            print(f"⚠️  {cic_col:30s} NOT FOUND")
    
    if len(available_features) < 6:
        print("\n❌ Not enough features found. Using alternative mapping...")
        # Alternative mapping using available columns
        alt_mapping = {
            'Flow Duration': 'duration',
            'Total Fwd Packets': 'pkts_toserver',
            'Total Backward Packets': 'bytes_toclient',
            'Total Length of Fwd Packets': 'bytes_toserver',
            'Total Length of Bwd Packets': 'bytes_toclient',
            'Flow Bytes/s': 'severity',
            'Flow Packets/s': 'pkts_toserver',
            'Fwd Packet Length Mean': 'bytes_toserver'
        }
        
        X = pd.DataFrame()
        for cic_col, hids_col in alt_mapping.items():
            if cic_col in data.columns:
                X[hids_col] = data[cic_col]
        
        # Fill missing features with defaults
        if 'src_port' not in X.columns:
            X['src_port'] = 0
        if 'dest_port' not in X.columns:
            X['dest_port'] = 80  # Default HTTP
        if 'proto' not in X.columns:
            X['proto'] = 1  # Default TCP
        
    else:
        # Extract features
        X = data[list(available_features.keys())].copy()
        X.columns = list(available_features.values())
    
    # Ensure we have exactly 8 features
    required_features = ['src_port', 'dest_port', 'duration', 'bytes_toserver', 
                        'bytes_toclient', 'pkts_toserver', 'proto', 'severity']
    
    for feat in required_features:
        if feat not in X.columns:
            X[feat] = 0
    
    X = X[required_features]
    
    # Handle missing values and infinities
    X = X.replace([np.inf, -np.inf], 0)
    X = X.fillna(0)
    
    # Encode protocol if needed
    if X['proto'].dtype == 'object':
        X['proto'] = X['proto'].map({'TCP': 1, 'UDP': 2, 'ICMP': 3}).fillna(1)
    
    print(f"\n✅ Feature matrix shape: {X.shape}")
    print(f"   Features: {list(X.columns)}")
    
    return X

def extract_labels(data):
    """Extract binary labels from CIC-IDS2017"""
    # Clean label column
    data.columns = data.columns.str.strip()
    
    # Find label column (may be 'Label' or ' Label')
    label_col = None
    for col in data.columns:
        if 'label' in col.lower():
            label_col = col
            break
    
    if label_col is None:
        print("❌ Label column not found!")
        return None
    
    print(f"\nLabel column: '{label_col}'")
    
    # Binary classification: BENIGN vs Attack
    y = (data[label_col].str.strip().str.upper() != 'BENIGN').astype(int)
    
    print(f"Normal (BENIGN): {(y==0).sum():,}")
    print(f"Attack: {(y==1).sum():,}")
    
    return y

def train_random_forest(X, y):
    """Train Random Forest classifier"""
    print("\n" + "=" * 70)
    print("Training Random Forest Classifier")
    print("=" * 70)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train):,} samples")
    print(f"  Normal: {(y_train==0).sum():,}")
    print(f"  Attack: {(y_train==1).sum():,}")
    print(f"\nTest set: {len(X_test):,} samples")
    print(f"  Normal: {(y_test==0).sum():,}")
    print(f"  Attack: {(y_test==1).sum():,}")
    
    # Scale features
    print("\nScaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("\nTraining Random Forest (this may take a few minutes)...")
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
    print("\n" + "=" * 70)
    print("Model Evaluation")
    print("=" * 70)
    
    y_pred = model.predict(X_test_scaled)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  True Negatives:  {cm[0,0]:,}")
    print(f"  False Positives: {cm[0,1]:,}")
    print(f"  False Negatives: {cm[1,0]:,}")
    print(f"  True Positives:  {cm[1,1]:,}")
    
    # Feature importance
    print("\nFeature Importance:")
    feature_names = ['src_port', 'dest_port', 'duration', 'bytes_toserver', 
                    'bytes_toclient', 'pkts_toserver', 'proto', 'severity']
    for feat, imp in sorted(zip(feature_names, model.feature_importances_), 
                           key=lambda x: x[1], reverse=True):
        print(f"  {feat:20s}: {imp:.4f} {'█' * int(imp * 50)}")
    
    return model, scaler

def save_model(model, scaler, output_dir='/home/jovyan/models'):
    """Save trained model for HIDS ML service"""
    print("\n" + "=" * 70)
    print("Saving Model")
    print("=" * 70)
    
    os.makedirs(output_dir, exist_ok=True)
    
    model_path = f'{output_dir}/anomaly_detector.pkl'
    scaler_path = f'{output_dir}/scaler.pkl'
    type_path = f'{output_dir}/model_type.txt'
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    with open(type_path, 'w') as f:
        f.write('random_forest_supervised')
    
    print(f"✅ Model saved: {model_path}")
    print(f"✅ Scaler saved: {scaler_path}")
    print(f"✅ Model type: random_forest_supervised")
    
    print("\n" + "=" * 70)
    print("Deployment Instructions")
    print("=" * 70)
    print("\n1. Copy models to HIDS:")
    print("   docker cp hids_jupyter:/home/jovyan/models/. ./hids/models/")
    print("\n2. Restart services:")
    print("   docker compose restart ml_service hids_engine")
    print("\n3. Test the system:")
    print("   python3 hids/test_mvp.py")
    print("\n4. Generate traffic:")
    print("   ./hids/generate_traffic.sh")

def main():
    print("=" * 70)
    print("CIC-IDS2017 Training Pipeline for HIDS")
    print("=" * 70)
    
    # Load data
    data = load_cicids2017_data()
    if data is None:
        print("\n❌ Failed to load dataset. Exiting.")
        return
    
    # Map features
    X = map_features_to_hids(data)
    if X is None:
        print("\n❌ Failed to map features. Exiting.")
        return
    
    # Extract labels
    y = extract_labels(data)
    if y is None:
        print("\n❌ Failed to extract labels. Exiting.")
        return
    
    # Train model
    model, scaler = train_random_forest(X, y)
    
    # Save model
    save_model(model, scaler)
    
    print("\n" + "=" * 70)
    print("✅ Training Complete!")
    print("=" * 70)

if __name__ == '__main__':
    main()
