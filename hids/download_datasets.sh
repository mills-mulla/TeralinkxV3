#!/bin/bash
# Download multiple IDS datasets including normal traffic

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Download IDS Datasets (CICIDS + NSL-KDD)              ║"
echo "╚════════════════════════════════════════════════════════════╝"

cd "$(dirname "$0")"
mkdir -p datasets

# Install Kaggle CLI if not present
if ! command -v kaggle &> /dev/null; then
    echo "Installing Kaggle CLI..."
    pip3 install kaggle
fi

echo ""
echo "IMPORTANT: Setup Kaggle API credentials first!"
echo "1. Go to: https://www.kaggle.com/settings"
echo "2. Click 'Create New API Token'"
echo "3. Save kaggle.json to: ~/.kaggle/kaggle.json"
echo "4. Run: chmod 600 ~/.kaggle/kaggle.json"
echo ""
read -p "Have you set up Kaggle credentials? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please setup Kaggle credentials first, then run this script again."
    exit 1
fi

cd datasets

# 1. NSL-KDD Dataset (has good normal traffic baseline)
echo ""
echo "════════════════════════════════════════════════════════════"
echo "Downloading NSL-KDD Dataset..."
echo "════════════════════════════════════════════════════════════"
kaggle datasets download -d hassan06/nslkdd
unzip -o nslkdd.zip
rm nslkdd.zip

# 2. CICIDS2017 (if not already present)
echo ""
echo "════════════════════════════════════════════════════════════"
echo "Downloading CICIDS2017..."
echo "════════════════════════════════════════════════════════════"
if [ ! -f "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" ]; then
    kaggle datasets download -d cicdataset/cicids2017
    unzip -o cicids2017.zip
    rm cicids2017.zip
else
    echo "✓ CICIDS2017 already exists"
fi

# 3. CICIDS2018
echo ""
echo "════════════════════════════════════════════════════════════"
echo "Downloading CICIDS2018..."
echo "════════════════════════════════════════════════════════════"
kaggle datasets download -d solarmainframe/ids-intrusion-csv
unzip -o ids-intrusion-csv.zip
rm ids-intrusion-csv.zip

# 4. UNSW-NB15 (another good dataset with normal traffic)
echo ""
echo "════════════════════════════════════════════════════════════"
echo "Downloading UNSW-NB15..."
echo "════════════════════════════════════════════════════════════"
kaggle datasets download -d mrwellsdavid/unsw-nb15
unzip -o unsw-nb15.zip
rm unsw-nb15.zip

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ DOWNLOAD COMPLETE                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Downloaded datasets:"
echo "  ✓ NSL-KDD (normal + attacks)"
echo "  ✓ CICIDS2017 (DDoS, port scans, brute force)"
echo "  ✓ CICIDS2018 (web attacks, infiltration)"
echo "  ✓ UNSW-NB15 (modern attacks + normal)"
echo ""
echo "Next: Run training script"
echo "  ./train_comprehensive.sh"
