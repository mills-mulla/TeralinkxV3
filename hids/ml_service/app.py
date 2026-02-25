from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

MODEL_PATH = '/app/models/anomaly_detector.pkl'

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    # ML prediction logic here
    return jsonify({'prediction': 'normal', 'confidence': 0.95}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
