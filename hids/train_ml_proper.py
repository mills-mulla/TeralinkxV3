#!/usr/bin/env python3
"""
HIDS ML Model Training - Proper Implementation
Three approaches: Simple, Balanced, Advanced
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

# ============================================================================
# APPROACH 1: TUNED ISOLATION FOREST (Unsupervised - Quick Fix)
# ============================================================================
def train_isolation_forest_tuned():
    """
    Best for: Quick deployment, no labeled data needed
    Pros: Fast, works with normal traffic only
    Cons: Higher false positives, can't learn attack patterns
    """
    print("\n" + "="*70)
    print("APPROACH 1: Tuned Isolation Forest (Unsupervised)")
    print("="*70)
    
    # Load NSL-KDD
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
    
    train_df = pd.read_csv('/home/jovyan/datasets/KDDTrain+.txt', names=columns)
    test_df = pd.read_csv('/home/jovyan/datasets/KDDTest+.txt', names=columns)
    
    # 8 features matching HIDS engine
    feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count',
                    'serror_rate', 'srv_serror_rate', 'same_srv_rate']
    
    # Train on NORMAL traffic only
    X_train_normal = train_df[train_df['label'] == 'normal'][feature_cols]
    X_test = test_df[feature_cols]
    y_test = (test_df['label'] != 'normal').astype(int)
    
    print(f"Training samples (normal): {len(X_train_normal)}")
    print(f"Test samples: {len(X_test)} ({y_test.sum()} attacks)")
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_normal)
    X_test_scaled = scaler.transform(X_test)
    
    # KEY TUNING: Lower contamination = fewer false positives
    model = IsolationForest(
        contamination=0.05,      # Expect only 5% anomalies (was 0.1)
        random_state=42,
        n_estimators=200,        # More trees = better accuracy
        max_samples=256,         # Subsample size
        max_features=1.0,        # Use all features
        bootstrap=False
    )
    
    model.fit(X_train_scaled)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_pred_binary = (y_pred == -1).astype(int)
    
    print("\nResults:")
    print(classification_report(y_test, y_pred_binary, target_names=['Normal', 'Attack']))
    
    return model, scaler, 'isolation_forest_tuned'


# ============================================================================
# APPROACH 2: RANDOM FOREST CLASSIFIER (Supervised - RECOMMENDED)
# ============================================================================
def train_random_forest_supervised():
    """
    Best for: Production use, best accuracy
    Pros: Learns attack patterns, low false positives, explainable
    Cons: Needs labeled data
    """
    print("\n" + "="*70)
    print("APPROACH 2: Random Forest Classifier (Supervised) - RECOMMENDED")
    print("="*70)
    
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
    
    train_df = pd.read_csv('/home/jovyan/datasets/KDDTrain+.txt', names=columns)
    test_df = pd.read_csv('/home/jovyan/datasets/KDDTest+.txt', names=columns)
    
    # Binary labels
    train_df['is_attack'] = (train_df['label'] != 'normal').astype(int)
    test_df['is_attack'] = (test_df['label'] != 'normal').astype(int)
    
    feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count',
                    'serror_rate', 'srv_serror_rate', 'same_srv_rate']
    
    X_train = train_df[feature_cols]
    y_train = train_df['is_attack']
    X_test = test_df[feature_cols]
    y_test = test_df['is_attack']
    
    print(f"Training samples: {len(X_train)} (Normal: {(y_train==0).sum()}, Attack: {(y_train==1).sum()})")
    print(f"Test samples: {len(X_test)} (Normal: {(y_test==0).sum()}, Attack: {(y_test==1).sum()})")
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        min_samples_leaf=4,
        class_weight='balanced',  # Handle imbalanced data
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    
    print("\nResults:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Attack']))
    
    # Feature importance
    print("\nFeature Importance:")
    for feat, imp in zip(feature_cols, model.feature_importances_):
        print(f"  {feat:20s}: {imp:.4f}")
    
    return model, scaler, 'random_forest_supervised'


# ============================================================================
# APPROACH 3: HYBRID ENSEMBLE (Advanced - Best Performance)
# ============================================================================
def train_hybrid_ensemble():
    """
    Best for: Maximum accuracy, research
    Pros: Combines multiple models, best detection rate
    Cons: More complex, slower inference
    """
    print("\n" + "="*70)
    print("APPROACH 3: Hybrid Ensemble (Advanced)")
    print("="*70)
    
    # Use Approach 2 as base
    rf_model, scaler, _ = train_random_forest_supervised()
    
    # Add Isolation Forest for novelty detection
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
    
    train_df = pd.read_csv('/home/jovyan/datasets/KDDTrain+.txt', names=columns)
    feature_cols = ['duration', 'src_bytes', 'dst_bytes', 'count', 'srv_count',
                    'serror_rate', 'srv_serror_rate', 'same_srv_rate']
    
    X_train_normal = train_df[train_df['label'] == 'normal'][feature_cols]
    X_train_scaled = scaler.transform(X_train_normal)
    
    if_model = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
    if_model.fit(X_train_scaled)
    
    # Save both models
    ensemble = {
        'random_forest': rf_model,
        'isolation_forest': if_model,
        'scaler': scaler
    }
    
    print("\n✅ Ensemble model created (RF + IF)")
    return ensemble, scaler, 'hybrid_ensemble'


# ============================================================================
# SAVE AND DEPLOY
# ============================================================================
def save_model(model, scaler, model_type):
    """Save model for ML service"""
    os.makedirs('/home/jovyan/models', exist_ok=True)
    
    if model_type == 'hybrid_ensemble':
        joblib.dump(model, '/home/jovyan/models/ensemble.pkl')
    else:
        joblib.dump(model, '/home/jovyan/models/anomaly_detector.pkl')
    
    joblib.dump(scaler, '/home/jovyan/models/scaler.pkl')
    
    with open('/home/jovyan/models/model_type.txt', 'w') as f:
        f.write(model_type)
    
    print(f"\n✅ Model saved: {model_type}")
    print("Copy to ML service:")
    print("  docker cp hids_jupyter:/home/jovyan/models/. ./hids/models/")
    print("  docker compose restart ml_service hids_engine")


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    print("="*70)
    print("HIDS ML Model Training Suite")
    print("="*70)
    
    print("\nChoose training approach:")
    print("1. Tuned Isolation Forest (Quick, unsupervised)")
    print("2. Random Forest Classifier (RECOMMENDED, supervised)")
    print("3. Hybrid Ensemble (Advanced, best performance)")
    
    choice = input("\nEnter choice (1/2/3) [default: 2]: ").strip() or '2'
    
    if choice == '1':
        model, scaler, model_type = train_isolation_forest_tuned()
    elif choice == '2':
        model, scaler, model_type = train_random_forest_supervised()
    elif choice == '3':
        model, scaler, model_type = train_hybrid_ensemble()
    else:
        print("Invalid choice!")
        exit(1)
    
    save_model(model, scaler, model_type)
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print("\nNext steps:")
    print("1. Copy models: docker cp hids_jupyter:/home/jovyan/models/. ./hids/models/")
    print("2. Restart services: docker compose restart ml_service hids_engine")
    print("3. Test: python3 hids/test_mvp.py")
