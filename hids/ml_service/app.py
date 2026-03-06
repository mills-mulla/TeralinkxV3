from flask import Flask, request, jsonify
import joblib
import numpy as np
import os
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from collections import deque
from datetime import datetime
import json

app = Flask(__name__)

MODEL_PATH = '/app/models/anomaly_detector.pkl'
SCALER_PATH = '/app/models/scaler.pkl'
MODEL_TYPE_PATH = '/app/models/model_type.txt'

model = None
scaler = None
model_type = 'isolation_forest'

# Advanced ML tracking
prediction_history = deque(maxlen=1000)
attack_patterns = {}
ip_reputation = {}

def load_or_create_model():
    """Load existing model or create new one"""
    global model, scaler, model_type
    
    os.makedirs('/app/models', exist_ok=True)
    
    # Check model type
    if os.path.exists(MODEL_TYPE_PATH):
        with open(MODEL_TYPE_PATH, 'r') as f:
            model_type = f.read().strip()
    
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        print(f"Loading existing model ({model_type})...")
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print(f"✅ Model loaded: {type(model).__name__}")
    else:
        print("⚠️  No trained model found. Creating default...")
        model = IsolationForest(
            contamination=0.05,
            random_state=42,
            n_estimators=100
        )
        scaler = StandardScaler()
        
        # Train on dummy data initially
        dummy_data = np.random.randn(100, 8)
        scaler.fit(dummy_data)
        model.fit(scaler.transform(dummy_data))
        
        # Save model
        joblib.dump(model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
        print("⚠️  Default model created. Train properly with: docker exec hids_jupyter python3 /home/jovyan/train_ml_proper.py")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model_loaded': model is not None}), 200

@app.route('/predict', methods=['POST'])
def predict():
    """Predict if network event is anomalous with enhanced analytics"""
    data = request.json
    
    if not data or 'features' not in data:
        return jsonify({'error': 'features array required'}), 400
    
    try:
        features = np.array(data['features']).reshape(1, -1)
        
        if features.shape[1] != 8:
            return jsonify({'error': 'Expected 8 features'}), 400
        
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Predict based on model type
        if isinstance(model, RandomForestClassifier):
            prediction = model.predict(features_scaled)[0]
            proba = model.predict_proba(features_scaled)[0]
            
            is_anomaly = prediction == 1
            confidence = proba[1] if is_anomaly else proba[0]
            
            result = {
                'prediction': 'anomaly' if is_anomaly else 'normal',
                'confidence': float(confidence),
                'model_type': 'supervised',
                'attack_class': get_attack_class(features[0]) if is_anomaly else None,
                'risk_score': calculate_risk_score(features[0], confidence)
            }
        else:
            prediction = model.predict(features_scaled)[0]
            score = model.score_samples(features_scaled)[0]
            
            is_anomaly = prediction == -1
            confidence = abs(score)
            
            result = {
                'prediction': 'anomaly' if is_anomaly else 'normal',
                'confidence': float(confidence),
                'anomaly_score': float(score),
                'model_type': 'unsupervised',
                'risk_score': calculate_risk_score(features[0], confidence)
            }
        
        # Track prediction
        prediction_history.append({
            'timestamp': datetime.now().isoformat(),
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'features': features[0].tolist()
        })
        
        # Update IP reputation if provided
        if 'src_ip' in data:
            update_ip_reputation(data['src_ip'], is_anomaly)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_attack_class(features):
    """Classify attack type based on features"""
    src_port, dest_port, duration, orig_bytes, resp_bytes, pkts, proto, severity = features
    
    # Port scan detection
    if pkts < 5 and orig_bytes < 100:
        return 'Port Scan'
    
    # DDoS detection
    if pkts > 100 or orig_bytes > 50000:
        return 'DDoS'
    
    # Brute force
    if dest_port in [22, 23, 3389, 21] and pkts > 10:
        return 'Brute Force'
    
    # Data exfiltration
    if orig_bytes > 10000 and duration > 60:
        return 'Data Exfiltration'
    
    return 'Unknown Attack'

def calculate_risk_score(features, confidence):
    """Calculate comprehensive risk score (0-100)"""
    src_port, dest_port, duration, orig_bytes, resp_bytes, pkts, proto, severity = features
    
    risk = confidence * 50  # Base from ML confidence
    
    # Add risk factors
    if dest_port in [22, 23, 3389, 445, 139]:  # Critical ports
        risk += 15
    if orig_bytes > 10000 or resp_bytes > 10000:  # Large transfers
        risk += 10
    if pkts > 100:  # High packet count
        risk += 10
    if duration > 300:  # Long connections
        risk += 10
    if severity <= 2:  # High severity
        risk += 5
    
    return min(100, risk)

def update_ip_reputation(ip, is_malicious):
    """Track IP reputation over time"""
    if ip not in ip_reputation:
        ip_reputation[ip] = {'malicious': 0, 'benign': 0, 'score': 50}
    
    if is_malicious:
        ip_reputation[ip]['malicious'] += 1
    else:
        ip_reputation[ip]['benign'] += 1
    
    total = ip_reputation[ip]['malicious'] + ip_reputation[ip]['benign']
    ip_reputation[ip]['score'] = (ip_reputation[ip]['malicious'] / total) * 100

@app.route('/analytics', methods=['GET'])
def analytics():
    """Get ML analytics from database"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'db'),
            database=os.getenv('POSTGRES_DB', 'hids'),
            user=os.getenv('POSTGRES_USER', 'hids'),
            password=os.getenv('POSTGRES_PASSWORD', 'hidspass')
        )
        cur = conn.cursor()
        
        # Total predictions
        cur.execute("SELECT COUNT(*) FROM ml_predictions")
        total = cur.fetchone()[0]
        
        # Recent predictions (last 100)
        cur.execute("""
            SELECT prediction, confidence 
            FROM ml_predictions 
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        recent = cur.fetchall()
        
        anomaly_count = sum(1 for p in recent if p[0] == 'anomaly')
        normal_count = len(recent) - anomaly_count
        avg_confidence = np.mean([p[1] for p in recent]) if recent else 0
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_predictions': total,
            'recent_anomalies': anomaly_count,
            'recent_normal': normal_count,
            'anomaly_rate': (anomaly_count / len(recent) * 100) if recent else 0,
            'avg_confidence': float(avg_confidence),
            'model_type': model_type,
            'top_malicious_ips': []
        }), 200
    except Exception as e:
        print(f"Analytics error: {e}")
        return jsonify({
            'total_predictions': 0,
            'recent_anomalies': 0,
            'recent_normal': 0,
            'anomaly_rate': 0,
            'avg_confidence': 0,
            'model_type': model_type,
            'top_malicious_ips': []
        }), 200

@app.route('/ip-reputation/<ip>', methods=['GET'])
def get_ip_reputation(ip):
    """Get reputation score for specific IP"""
    if ip in ip_reputation:
        return jsonify(ip_reputation[ip]), 200
    return jsonify({'score': 50, 'malicious': 0, 'benign': 0}), 200

@app.route('/train', methods=['POST'])
def train():
    """Retrain model with new data"""
    data = request.json
    
    if not data or 'training_data' not in data:
        return jsonify({'error': 'training_data array required'}), 400
    
    try:
        training_data = np.array(data['training_data'])
        
        if training_data.shape[1] != 8:
            return jsonify({'error': 'Expected 8 features per sample'}), 400
        
        # Retrain
        scaler.fit(training_data)
        model.fit(scaler.transform(training_data))
        
        # Save updated model
        joblib.dump(model, MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
        
        return jsonify({
            'message': 'Model retrained successfully',
            'samples': len(training_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    load_or_create_model()
    app.run(host='0.0.0.0', port=5001)
