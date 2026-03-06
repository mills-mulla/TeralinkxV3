#!/usr/bin/env python3
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

print("Creating baseline model...")

# Create synthetic training data (normal vs attack patterns)
np.random.seed(42)
n_samples = 5000

# Normal traffic: low values, consistent patterns
normal = np.random.normal([0, 0, 1, 500, 500, 10, 1, 1], [10, 10, 0.5, 200, 200, 5, 0.1, 0.1], (n_samples, 8))

# Attack traffic: high values, erratic patterns  
attack = np.random.normal([0, 0, 10, 5000, 5000, 100, 1, 3], [50, 50, 5, 2000, 2000, 50, 0.5, 1], (n_samples, 8))

X = np.vstack([normal, attack])
y = np.hstack([np.zeros(n_samples), np.ones(n_samples)])

print(f"Training on {len(X):,} synthetic samples...")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
model.fit(X_scaled, y)

print(f"Training accuracy: {model.score(X_scaled, y):.2%}")

os.makedirs('/app/models', exist_ok=True)
joblib.dump(model, '/app/models/anomaly_detector.pkl')
joblib.dump(scaler, '/app/models/scaler.pkl')

with open('/app/models/model_type.txt', 'w') as f:
    f.write('random_forest_baseline')

print("\n✅ Baseline model saved to /app/models/")
