#!/bin/bash
# Download CIC-IDS2017 Dataset
# Official: https://www.unb.ca/cic/datasets/ids-2017.html
# Alternative mirrors and sources

PCAP_DIR="./hids/pcaps"
DATASET_DIR="./hids/datasets"
mkdir -p "$PCAP_DIR" "$DATASET_DIR"

echo "=== CIC-IDS2017 Dataset Downloader ==="
echo ""

# Method 1: Kaggle (requires kaggle API)
echo "Method 1: Trying Kaggle..."
if command -v kaggle &> /dev/null; then
    echo "Downloading from Kaggle..."
    kaggle datasets download -d cicdataset/cicids2017 -p "$DATASET_DIR" --unzip
else
    echo "Kaggle CLI not installed. Install: pip install kaggle"
    echo "Setup: https://github.com/Kaggle/kaggle-api#api-credentials"
fi

echo ""
echo "Method 2: Direct download from mirrors..."

# AWS Open Data mirror
echo "Trying AWS Open Data Registry..."
wget -c -O "$DATASET_DIR/cicids2017.zip" \
    "https://cloudstor.aarnet.edu.au/plus/s/2DhnLGDdEECo4ys/download" \
    2>&1 | grep -E "saved|failed|error" || true

# Alternative: Download CSV files (processed features)
echo ""
echo "Downloading processed CSV files..."
BASE_URL="https://raw.githubusercontent.com/defcom17/CIC-IDS2017/main"

wget -c -O "$DATASET_DIR/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" \
    "$BASE_URL/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" 2>&1 | tail -1

wget -c -O "$DATASET_DIR/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv" \
    "$BASE_URL/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv" 2>&1 | tail -1

echo ""
echo "Method 3: Download sample PCAPs from tcpreplay..."
wget -c -O "$PCAP_DIR/bigFlows.pcap" \
    "https://s3.amazonaws.com/tcpreplay-pcap-files/bigFlows.pcap" 2>&1 | tail -1

wget -c -O "$PCAP_DIR/smallFlows.pcap" \
    "https://s3.amazonaws.com/tcpreplay-pcap-files/smallFlows.pcap" 2>&1 | tail -1

echo ""
echo "=== Download Summary ==="
echo "PCAP files:"
ls -lh "$PCAP_DIR"/*.pcap 2>/dev/null || echo "  No PCAP files"

echo ""
echo "CSV files:"
ls -lh "$DATASET_DIR"/*.csv 2>/dev/null || echo "  No CSV files"

echo ""
echo "=== Manual Download Instructions ==="
echo "1. Visit: https://www.unb.ca/cic/datasets/ids-2017.html"
echo "2. Download PCAP files to: $PCAP_DIR/"
echo "3. Or use Kaggle: https://www.kaggle.com/datasets/cicdataset/cicids2017"
echo ""
echo "For Kaggle download:"
echo "  pip install kaggle"
echo "  kaggle datasets download -d cicdataset/cicids2017"
