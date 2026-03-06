#!/usr/bin/env python3
"""
Balanced HIDS Training Script
Trains on BOTH normal traffic (your network) AND attack traffic (CICIDS2017)
to reduce false positive rate and bias
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
import psycopg2
from datetime import datetime, timedelta

def collect_normal_traffic_from_db(days=7):
    """Collect normal traffic baseline from your network"""
    print("=" * 70)
    print("Collecting Normal Traffic Baseline from Your Network")
    print("=" * 70)
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'hids'),
            user=os.getenv('POSTGRES_USER', 'hids'),
            password=os.getenv('POSTGRES_PASSWORD', 'hidspass')
        )
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT 
                src_port, dest_port, 
                COALESCE(duration, 0) as duration,
                COALESCE(orig_bytes, 0) as bytes_toserver,
                COALESCE(resp_bytes, 0) as bytes_toclient,
                1 as pkts_toserver,
                CASE 
                    WHEN proto = 'tcp' THEN 1
                    WHEN proto = 'udp' THEN 2
                    ELSE 3
                END as proto,
                1 as severity
            FROM zeek_connections
            WHERE timestamp > %s
            AND conn_state NOT IN ('REJ', 'RSTO', 'RSTOS0')
            LIMIT 50000
        """
        
        df = pd.read_sql(query, conn, params=(cutoff_date,))
        conn.close()
        
        if len(df) > 0:
            print(f"✅ Collected {len(df):,} normal traffic samples from your network")
            return df
        else:
            print("⚠️  No normal traffic found in database")
            return None
            
    except Exception as e:
        print(f"⚠️  Could not connect to database: {e}")
        print("   Using synthetic normal traffic instead...")
        return generate_synthetic_normal_traffic()

def generate_synthetic_normal_traffic(n_samples=20000):
    """Generate synthetic normal traffic patterns"""
    print(f"\nGenerating {n_samples:,} synthetic normal traffic samples...")
    
    np.random.seed(42)
    normal_patterns = []
    
    # HTTP/HTTPS traffic (25%)
    for _ in range(n_samples // 4):
        normal_patterns.append([
            np.random.randint(1024, 65535),
            np.random.choice([80, 443]),
            np.random.uniform(0.1, 30),
            np.random.randint(100, 5000),
            np.random.randint(500, 50000),
            np.random.randint(5, 50),
            1, 3
        ])
    
    # DNS traffic (25%)
    for _ in range(n_samples // 4):
        normal_patterns.append([
            np.random.randint(1024, 65535), 53,
            np.random.uniform(0.01, 1),
            np.random.randint(50, 200),
            np.random.randint(50, 500),
            np.random.randint(1, 5),
            2, 3
        ])
    
    # SSH legitimate sessions (25%)
    for _ in range(n_samples // 4):
        normal_patterns.append([
            np.random.randint(1024, 65535), 22,
            np.random.uniform(60, 3600),
            np.random.randint(1000, 10000),
            np.random.randint(1000, 10000),
            np.random.randint(50, 500),
            1, 3
        ])
    
    # Other services (25%)
    for _ in range(n_samples // 4):
        normal_patterns.append([
            np.random.randint(1024, 65535),
            np.random.choice([25, 110, 143, 21, 3306, 5432]),
            np.random.uniform(1, 300),
            np.random.randint(100, 5000),
            np.random.randint(100, 5000),
            np.random.randint(10, 100),
            1, 3
        ])
    
    df = pd.DataFrame(normal_patterns, columns=[
        'src_port', 'dest_port', 'duration', 'bytes_toserver',
        'bytes_toclient', 'pkts_toserver', 'proto', 'severity'
    ])
    
    print(f"✅ Generated {len(df):,} synthetic normal traffic samples")
    return df

def load_cicids2017_attacks(dataset_path='/home/jovyan/datasets', max_samples=50000):
    """Load ONLY attack traffic from CICIDS2017"""
    print("\n" + "=" * 70)
    print("Loading Attack Traffic from CICIDS2017")
    print("=" * 70)
    
    csv_files = glob.glob(f'{dataset_path}/*ISCX.csv')
    
    if not csv_files:
        print(f"⚠️  No CICIDS2017 files found in {dataset_path}")
        return None
    
    print(f"Found {len(csv_files)} CSV files")
    attack_samples = []
    
    for file in csv_files[:3]:
        try:
            print(f"\nLoading {os.path.basename(file)}...")
            df = pd.read_csv(file, encoding='latin1', low_memory=False)
            df.columns = df.columns.str.strip()
            
            label_col = None
            for col in df.columns:
                if 'label' in col.lower():
                    label_col = col
                    break
            
            if label_col:
                attacks = df[df[label_col].str.strip().str.upper() != 'BENIGN']
                
                if len(attacks) > 0:
                    X = map_cicids_features(attacks)
                    attack_samples.append(X)
                    print(f"  Extracted {len(X):,} attack samples")
                    
                    if sum(len(a) for a in attack_samples) >= max_samples:
                        break
        except Exception as e:
            print(f"  Error: {e}")
    
    if attack_samples:
        attacks_df = pd.concat(attack_samples, ignore_index=True)
        attacks_df = attacks_df.sample(min(len(attacks_df), max_samples), random_state=42)
        print(f"\n✅ Total attack samples: {len(attacks_df):,}")
        return attacks_df
    
    return None

def map_cicids_features(data):
    """Map CICIDS2017 features to HIDS format"""
    X = pd.DataFrame()
    
    X['src_port'] = data['Source Port'] if 'Source Port' in data.columns else 0
    X['dest_port'] = data['Destination Port'] if 'Destination Port' in data.columns else 80
    X['duration'] = data['Flow Duration'] / 1000000 if 'Flow Duration' in data.columns else 0
    
    if 'Total Length of Fwd Packets' in data.columns:
        X['bytes_toserver'] = data['Total Length of Fwd Packets']
    elif 'Total Fwd Packets' in data.columns:
        X['bytes_toserver'] = data['Total Fwd Packets'] * 100
    else:
        X['bytes_toserver'] = 0
    
    if 'Total Length of Bwd Packets' in data.columns:
        X['bytes_toclient'] = data['Total Length of Bwd Packets']
    elif 'Total Backward Packets' in data.columns:
        X['bytes_toclient'] = data['Total Backward Packets'] * 100
    else:
        X['bytes_toclient'] = 0
    
    X['pkts_toserver'] = data['Total Fwd Packets'] if 'Total Fwd Packets' in data.columns else 1
    X['proto'] = 1
    X['severity'] = 1
    
    X = X.replace([np.inf, -np.inf], 0).fillna(0)
    return X

def train_balanced_model(normal_df, attack_df):
    """Train model on balanced dataset"""
    print("\n" + "=" * 70)
    print("Training Balanced Random Forest Model")
    print("=" * 70)
    
    normal_df['label'] = 0
    attack_df['label'] = 1
    
    min_samples = min(len(normal_df), len(attack_df))
    normal_balanced = normal_df.sample(min_samples, random_state=42)
    attack_balanced = attack_df.sample(min_samples, random_state=42)
    
    data = pd.concat([normal_balanced, attack_balanced], ignore_index=True)
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"\nBalanced Dataset:")
    print(f"  Normal traffic: {len(normal_balanced):,} samples")
    print(f"  Attack traffic: {len(attack_balanced):,} samples")
    print(f"  Total: {len(data):,} samples")
    print(f"  Balance ratio: 50/50 (PERFECT)")
    
    feature_cols = ['src_port', 'dest_port', 'duration', 'bytes_toserver',
                   'bytes_toclient', 'pkts_toserver', 'proto', 'severity']
    
    X = data[feature_cols]
    y = data['label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train):,} samples")
    print(f"  Normal: {(y_train==0).sum():,}")
    print(f"  Attack: {(y_train==1).sum():,}")
    
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
    
    print("\n" + "=" * 70)
    print("Model Evaluation")
    print("=" * 70)
    
    y_pred = model.predict(X_test_scaled)
    
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  True Negatives:  {cm[0,0]:,} (Correctly identified normal)")
    print(f"  False Positives: {cm[0,1]:,} (Normal flagged as attack) ⚠️")
    print(f"  False Negatives: {cm[1,0]:,} (Attack missed) ⚠️")
    print(f"  True Positives:  {cm[1,1]:,} (Correctly identified attack)")
    
    fpr = cm[0,1] / (cm[0,0] + cm[0,1]) * 100
    print(f"\n📊 False Positive Rate: {fpr:.2f}%")
    print(f"   (Industry target: <5%)")
    
    print("\nFeature Importance:")
    for feat, imp in sorted(zip(feature_cols, model.feature_importances_), 
                           key=lambda x: x[1], reverse=True):
        print(f"  {feat:20s}: {imp:.4f} {'█' * int(imp * 50)}")
    
    return model, scaler

def save_model(model, scaler, output_dir='./models'):
    """Save trained model"""
    print("\n" + "=" * 70)
    print("Saving Balanced Model")
    print("=" * 70)
    
    os.makedirs(output_dir, exist_ok=True)
    
    joblib.dump(model, f'{output_dir}/anomaly_detector.pkl')
    joblib.dump(scaler, f'{output_dir}/scaler.pkl')
    
    with open(f'{output_dir}/model_type.txt', 'w') as f:
        f.write('random_forest_balanced')
    
    print(f"✅ Model saved to {output_dir}/")

def main():
    print("=" * 70)
    print("BALANCED HIDS TRAINING PIPELINE")
    print("Reduces False Positives by Training on YOUR Normal Traffic")
    print("=" * 70)
    
    normal_df = collect_normal_traffic_from_db(days=7)
    
    if normal_df is None or len(normal_df) < 1000:
        print("\n⚠️  Not enough real traffic, using synthetic normal traffic")
        normal_df = generate_synthetic_normal_traffic(n_samples=20000)
    
    attack_df = load_cicids2017_attacks()
    
    if attack_df is None:
        print("\n❌ No attack data available. Cannot train.")
        return
    
    model, scaler = train_balanced_model(normal_df, attack_df)
    save_model(model, scaler)
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Deploy: docker cp ./models/. hids_ml_service:/app/models/")
    print("2. Restart: docker compose restart ml_service hids_engine")
    print("3. Expected: Anomaly rate 5-15% (down from 97%)")

if __name__ == '__main__':
    main()
