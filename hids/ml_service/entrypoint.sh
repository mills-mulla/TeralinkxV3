#!/bin/bash
set -e

echo "🚀 Starting HIDS ML Service..."
echo "Model Path: ${MODEL_PATH:-/app/models/anomaly_detector.pkl}"
echo "Database: ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-hids}"

# Extract connection details
DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
MODEL_DIR="/app/models"

# Create models directory if it doesn't exist
mkdir -p "$MODEL_DIR"

# Check if model exists
if [ ! -f "${MODEL_PATH:-/app/models/anomaly_detector.pkl}" ]; then
  echo "⚠️  No trained model found at ${MODEL_PATH:-/app/models/anomaly_detector.pkl}"
  echo "📦 Default model will be created on first startup"
  echo "ℹ️  For better accuracy, train the model with:"
  echo "   docker exec hids_jupyter python3 /home/jovyan/train_ml_proper.py"
else
  echo "✅ Trained model found!"
  
  # Check model type
  if [ -f "${MODEL_DIR}/model_type.txt" ]; then
    MODEL_TYPE=$(cat "${MODEL_DIR}/model_type.txt")
    echo "📊 Model Type: ${MODEL_TYPE}"
  fi
fi

# Wait for database (for analytics)
echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
attempt=1
max_attempts=30
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  if [[ $attempt -ge $max_attempts ]]; then
    echo "⚠️  Database not available after ${max_attempts} attempts"
    echo "   ML service will start but analytics will not work"
    break
  fi
  echo "  Database not ready, waiting... (attempt $attempt/$max_attempts)"
  sleep 2
  ((attempt++))
done

if nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; then
  echo "✅ Database is ready!"
  
  # Test database connection
  echo "Testing database connection..."
  python3 << END
import psycopg2
import os

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'hids'),
        user=os.getenv('POSTGRES_USER', 'hids'),
        password=os.getenv('POSTGRES_PASSWORD', 'hidspass')
    )
    conn.close()
    print('✅ Database connection successful!')
except Exception as e:
    print(f'⚠️  Database connection failed: {e}')
    print('   Analytics features will not work')
END
fi

# Validate model on startup
echo "🧪 Validating ML model..."
python3 << END
import os
import sys

MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/anomaly_detector.pkl')
SCALER_PATH = os.getenv('SCALER_PATH', '/app/models/scaler.pkl')

if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
    try:
        import joblib
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print(f'✅ Model loaded: {type(model).__name__}')
        print(f'✅ Scaler loaded: {type(scaler).__name__}')
    except Exception as e:
        print(f'⚠️  Model validation failed: {e}')
        print('   Default model will be created')
else:
    print('ℹ️  No existing model - will create default on startup')
END

echo "🎉 ML Service initialization complete!"
echo "🤖 Starting ML prediction service on port ${ML_SERVICE_PORT:-5001}..."

exec "$@"
