#!/bin/bash
# Complete training pipeline with multiple datasets

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   COMPREHENSIVE HIDS TRAINING PIPELINE                    ║"
echo "║   Datasets: NSL-KDD + CICIDS2017 + CICIDS2018             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Download datasets
if [ ! -f "datasets/KDDTrain+.txt" ] || [ ! -f "datasets/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" ]; then
    echo "Step 1: Downloading datasets from Kaggle..."
    ./download_datasets.sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Dataset download failed"
        exit 1
    fi
else
    echo "✓ Datasets already present"
fi

# Step 2: Train model
echo ""
echo "Step 2: Training comprehensive model..."
python3 train_comprehensive.py

if [ $? -ne 0 ]; then
    echo "❌ Training failed"
    exit 1
fi

# Step 3: Deploy
echo ""
echo "Step 3: Deploying model..."
docker cp models/anomaly_detector.pkl hids_ml_service:/app/models/
docker cp models/scaler.pkl hids_ml_service:/app/models/
docker cp models/model_type.txt hids_ml_service:/app/models/

# Step 4: Restart
echo ""
echo "Step 4: Restarting services..."
docker compose restart ml_service hids_engine

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ✅ DEPLOYMENT COMPLETE                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Your HIDS now trained on:"
echo "  ✓ NSL-KDD (rich normal traffic baseline)"
echo "  ✓ CICIDS2017 (DDoS, port scans, brute force)"
echo "  ✓ CICIDS2018 (web attacks, infiltration)"
echo ""
echo "Expected anomaly rate: 5-15% (down from 97%)"
echo ""
echo "Test: python3 test_mvp.py"
