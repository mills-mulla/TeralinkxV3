import psycopg2
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'hids')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'hids')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'hidspass')

def extract_features():
    """Extract features from Zeek connections for training"""
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    
    query = """
        SELECT 
            src_port, dest_port, duration, orig_bytes, resp_bytes,
            CASE 
                WHEN proto = 'tcp' THEN 1
                WHEN proto = 'udp' THEN 2
                WHEN proto = 'icmp' THEN 3
                ELSE 0
            END as proto_encoded
        FROM zeek_connections
        WHERE duration IS NOT NULL
        LIMIT 10000
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Fill missing values
    df = df.fillna(0)
    
    # Add derived features
    df['total_bytes'] = df['orig_bytes'] + df['resp_bytes']
    df['byte_ratio'] = df['orig_bytes'] / (df['resp_bytes'] + 1)
    
    return df.values

def train_model():
    """Train Isolation Forest model"""
    print("Extracting features from database...")
    
    try:
        features = extract_features()
        
        if len(features) < 100:
            print("Not enough data, using synthetic data...")
            features = np.random.randn(1000, 8)
        
        print(f"Training on {len(features)} samples...")
        
        # Scale features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Train Isolation Forest
        model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100,
            max_samples='auto'
        )
        model.fit(features_scaled)
        
        # Save model
        os.makedirs('/app/models', exist_ok=True)
        joblib.dump(model, '/app/models/anomaly_detector.pkl')
        joblib.dump(scaler, '/app/models/scaler.pkl')
        
        print("Model trained and saved successfully!")
        
    except Exception as e:
        print(f"Error training model: {e}")
        print("Creating default model...")
        
        # Create default model with synthetic data
        features = np.random.randn(1000, 8)
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(features_scaled)
        
        os.makedirs('/app/models', exist_ok=True)
        joblib.dump(model, '/app/models/anomaly_detector.pkl')
        joblib.dump(scaler, '/app/models/scaler.pkl')
        print("Default model created")

if __name__ == '__main__':
    train_model()
