#!/bin/bash
# Quick ML Model Training & Deployment

echo "=========================================="
echo "HIDS ML Model Training & Deployment"
echo "=========================================="
echo ""
echo "This will train a Random Forest Classifier (supervised learning)"
echo "on the NSL-KDD dataset for best accuracy and lowest false positives."
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "Step 1: Copying training script to Jupyter container..."
docker cp ./hids/train_ml_proper.py hids_jupyter:/home/jovyan/

echo ""
echo "Step 2: Training model (this may take 1-2 minutes)..."
docker exec hids_jupyter python3 /home/jovyan/train_ml_proper.py << EOF
2
EOF

echo ""
echo "Step 3: Copying trained model to ML service..."
docker cp hids_jupyter:/home/jovyan/models/anomaly_detector.pkl ./hids/models/
docker cp hids_jupyter:/home/jovyan/models/scaler.pkl ./hids/models/
docker cp hids_jupyter:/home/jovyan/models/model_type.txt ./hids/models/

echo ""
echo "Step 4: Rebuilding and restarting services..."
docker compose build ml_service
docker compose restart ml_service hids_engine

echo ""
echo "Step 5: Waiting for services to start..."
sleep 10

echo ""
echo "=========================================="
echo "✅ Training Complete!"
echo "=========================================="
echo ""
echo "Testing the new model..."
python3 hids/test_mvp.py

echo ""
echo "Access dashboard: http://localhost:5002"
echo "Check ML service: curl http://localhost:5001/health"
