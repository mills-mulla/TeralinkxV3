#!/bin/bash
# CIC-IDS2017 Training & Deployment Script for HIDS
# This script automates the entire ML training pipeline

set -e  # Exit on error

echo "=================================================================="
echo "CIC-IDS2017 HIDS ML Training Pipeline"
echo "=================================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
PROJECT_ROOT="/home/ghost/Desktop/TeralinkxV3"
DATASET_DIR="$PROJECT_ROOT/hids/datasets"
MODELS_DIR="$PROJECT_ROOT/hids/models"

cd "$PROJECT_ROOT"

# Step 1: Check if dataset exists
echo -e "\n${YELLOW}Step 1: Checking CIC-IDS2017 dataset...${NC}"
if ls "$DATASET_DIR"/*ISCX.csv 1> /dev/null 2>&1; then
    echo -e "${GREEN}✅ Found CIC-IDS2017 CSV files:${NC}"
    ls -lh "$DATASET_DIR"/*ISCX.csv | awk '{print "   " $9 " (" $5 ")"}'
else
    echo -e "${RED}❌ No CIC-IDS2017 files found in $DATASET_DIR${NC}"
    echo ""
    echo "You already have these files:"
    ls -lh "$DATASET_DIR"/*.csv 2>/dev/null || echo "  (none)"
    echo ""
    echo "To download more CIC-IDS2017 files, visit:"
    echo "  https://www.unb.ca/cic/datasets/ids-2017.html"
    echo ""
    read -p "Continue with existing files? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Check Docker containers
echo -e "\n${YELLOW}Step 2: Checking Docker containers...${NC}"
if ! docker ps | grep -q hids_jupyter; then
    echo -e "${RED}❌ hids_jupyter container not running${NC}"
    echo "Start HIDS with: docker compose up -d"
    exit 1
fi
echo -e "${GREEN}✅ Docker containers running${NC}"

# Step 3: Copy dataset to Jupyter container
echo -e "\n${YELLOW}Step 3: Copying dataset to Jupyter container...${NC}"
docker exec hids_jupyter mkdir -p /home/jovyan/datasets
for file in "$DATASET_DIR"/*.csv; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "  Copying $filename..."
        docker cp "$file" hids_jupyter:/home/jovyan/datasets/
    fi
done
echo -e "${GREEN}✅ Dataset copied${NC}"

# Step 4: Copy training script
echo -e "\n${YELLOW}Step 4: Copying training script...${NC}"
docker cp "$PROJECT_ROOT/hids/train_cicids2017_proper.py" hids_jupyter:/home/jovyan/
echo -e "${GREEN}✅ Training script copied${NC}"

# Step 5: Install dependencies
echo -e "\n${YELLOW}Step 5: Installing dependencies...${NC}"
docker exec hids_jupyter pip install -q pandas numpy scikit-learn joblib
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 6: Train model
echo -e "\n${YELLOW}Step 6: Training ML model (this may take 5-15 minutes)...${NC}"
echo "=================================================================="
docker exec hids_jupyter python3 /home/jovyan/train_cicids2017_proper.py
echo "=================================================================="

# Step 7: Copy trained model back
echo -e "\n${YELLOW}Step 7: Deploying trained model...${NC}"
mkdir -p "$MODELS_DIR"
docker cp hids_jupyter:/home/jovyan/models/anomaly_detector.pkl "$MODELS_DIR/"
docker cp hids_jupyter:/home/jovyan/models/scaler.pkl "$MODELS_DIR/"
docker cp hids_jupyter:/home/jovyan/models/model_type.txt "$MODELS_DIR/"
echo -e "${GREEN}✅ Model deployed to $MODELS_DIR${NC}"

# Step 8: Restart services
echo -e "\n${YELLOW}Step 8: Restarting HIDS services...${NC}"
docker compose restart ml_service hids_engine
sleep 3
echo -e "${GREEN}✅ Services restarted${NC}"

# Step 9: Verify deployment
echo -e "\n${YELLOW}Step 9: Verifying deployment...${NC}"
if docker exec hids_ml_service ls /app/models/anomaly_detector.pkl > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Model loaded in ML service${NC}"
else
    echo -e "${RED}⚠️  Model not found in ML service${NC}"
fi

# Check ML service health
if curl -s http://localhost:5001/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ ML service is healthy${NC}"
else
    echo -e "${RED}⚠️  ML service health check failed${NC}"
fi

# Summary
echo ""
echo "=================================================================="
echo -e "${GREEN}✅ Training & Deployment Complete!${NC}"
echo "=================================================================="
echo ""
echo "Your HIDS is now trained on CIC-IDS2017 dataset!"
echo ""
echo "Next steps:"
echo "  1. Test the system:"
echo "     python3 hids/test_mvp.py"
echo ""
echo "  2. Generate test traffic:"
echo "     ./hids/generate_traffic.sh"
echo ""
echo "  3. View dashboard:"
echo "     http://localhost:5000"
echo ""
echo "  4. Check logs:"
echo "     docker compose logs -f hids_engine ml_service"
echo ""
echo "Model details:"
echo "  Type: Random Forest (Supervised)"
echo "  Dataset: CIC-IDS2017"
echo "  Features: 8 (matching HIDS engine)"
echo "  Location: $MODELS_DIR"
echo ""
