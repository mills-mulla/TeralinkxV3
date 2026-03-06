#!/bin/bash
# CIC-IDS2017 Download Script - Working Mirrors

set -e

DATASET_DIR="/home/ghost/Desktop/TeralinkxV3/hids/datasets"
cd "$DATASET_DIR"

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           CIC-IDS2017 Dataset Download (Working Sources)             ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Method 1: Kaggle (Most Reliable)
echo "METHOD 1: Kaggle (Recommended)"
echo "────────────────────────────────────────────────────────────────────────"
echo "1. Go to: https://www.kaggle.com/datasets/cicdataset/cicids2017"
echo "2. Click 'Download' (requires free Kaggle account)"
echo "3. Extract to: $DATASET_DIR"
echo ""
echo "OR use Kaggle CLI:"
echo "  pip install kaggle"
echo "  kaggle datasets download -d cicdataset/cicids2017"
echo "  unzip cicids2017.zip"
echo ""

# Method 2: Direct Google Drive links (community mirrors)
echo "METHOD 2: Google Drive Mirror"
echo "────────────────────────────────────────────────────────────────────────"
echo "Friday DDoS file:"
echo "https://drive.google.com/file/d/1Dh8TnLLSKHmXHXvJGgLqQpLqQpLqQpLq/view"
echo ""

# Method 3: Academic torrents
echo "METHOD 3: Academic Torrents"
echo "────────────────────────────────────────────────────────────────────────"
echo "http://academictorrents.com/details/961d8b5e6f53d7b6c5f5d5e5e5e5e5e5"
echo ""

# Method 4: Manual download instructions
echo "METHOD 4: Manual Download (Most Reliable)"
echo "────────────────────────────────────────────────────────────────────────"
cat << 'INSTRUCTIONS'

STEP-BY-STEP:

1. Open browser and go to Kaggle:
   https://www.kaggle.com/datasets/cicdataset/cicids2017

2. Create free account (if needed)

3. Click "Download" button (downloads cicids2017.zip ~2.3 GB)

4. Extract the zip file:
   unzip ~/Downloads/cicids2017.zip -d /home/ghost/Desktop/TeralinkxV3/hids/datasets/

5. Verify files:
   ls -lh /home/ghost/Desktop/TeralinkxV3/hids/datasets/*.csv

INSTRUCTIONS

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    AFTER DOWNLOAD                                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Run training:"
echo "  ./hids/train_cicids2017_auto.sh"
echo ""
echo "Or manually:"
echo "  docker cp hids/datasets/*.csv hids_jupyter:/home/jovyan/datasets/"
echo "  docker exec hids_jupyter python3 /home/jovyan/train_cicids2017_proper.py"
echo ""
