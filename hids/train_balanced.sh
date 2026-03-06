#!/bin/bash

echo "=========================================="
echo "HIDS Balanced Training Script"
echo "Fixes High Anomaly Rate by Training on Normal Traffic"
echo "=========================================="

cd "$(dirname "$0")"

# Check if datasets exist
if [ ! -d "datasets" ] || [ -z "$(ls -A datasets/*.csv 2>/dev/null)" ]; then
    echo ""
    echo "⚠️  CICIDS2017 dataset not found!"
    echo "   Downloading now (this may take a while)..."
    ./download_cicids2017.sh
fi

# Run training
echo ""
echo "Starting balanced training..."
echo ""

python3 train_balanced.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Training Complete!"
    echo "=========================================="
    echo ""
    echo "Deploying model to ML service..."
    
    # Copy models to ML service
    if [ -d "models" ]; then
        docker cp models/anomaly_detector.pkl hids_ml_service:/app/models/
        docker cp models/scaler.pkl hids_ml_service:/app/models/
        docker cp models/model_type.txt hids_ml_service:/app/models/
        
        echo "✅ Models deployed"
        echo ""
        echo "Restarting services..."
        docker compose restart ml_service hids_engine
        
        echo ""
        echo "=========================================="
        echo "✅ HIDS Updated Successfully!"
        echo "=========================================="
        echo ""
        echo "Your anomaly rate should now be 5-15% instead of 97%"
        echo ""
        echo "Test it:"
        echo "  python3 test_mvp.py"
        echo ""
    else
        echo "⚠️  Models directory not found"
    fi
else
    echo ""
    echo "❌ Training failed. Check errors above."
fi
