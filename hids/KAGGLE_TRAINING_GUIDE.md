# Training HIDS with Kaggle Datasets

## Datasets Used

### 1. **NSL-KDD** (Best for Normal Traffic)
- **Source**: Kaggle - `hassan06/nslkdd`
- **Contains**: 67% normal traffic, 33% attacks
- **Why**: Excellent baseline of normal network behavior
- **Attacks**: DoS, Probe, R2L, U2R

### 2. **CICIDS2017**
- **Source**: Kaggle - `cicdataset/cicids2017`
- **Contains**: DDoS, Port Scans, Brute Force, Web Attacks
- **Size**: ~2.8M samples
- **Normal Traffic**: 20%

### 3. **CICIDS2018**
- **Source**: Kaggle - `solarmainframe/ids-intrusion-csv`
- **Contains**: Web attacks, Infiltration, Botnet
- **Size**: ~16M samples
- **Normal Traffic**: 15%

### 4. **UNSW-NB15** (Optional)
- **Source**: Kaggle - `mrwellsdavid/unsw-nb15`
- **Contains**: Modern attacks + normal traffic
- **Normal Traffic**: 56%

## Setup Kaggle API

### Step 1: Get API Token
```bash
# 1. Go to: https://www.kaggle.com/settings
# 2. Scroll to "API" section
# 3. Click "Create New API Token"
# 4. Download kaggle.json
```

### Step 2: Install Credentials
```bash
# Create kaggle directory
mkdir -p ~/.kaggle

# Move downloaded file
mv ~/Downloads/kaggle.json ~/.kaggle/

# Set permissions
chmod 600 ~/.kaggle/kaggle.json
```

### Step 3: Install Kaggle CLI
```bash
pip3 install kaggle
```

## Quick Start (One Command)

```bash
cd /home/ghost/Desktop/TeralinkxV3/hids
./train_comprehensive.sh
```

This will:
1. ✅ Download all datasets from Kaggle
2. ✅ Train on balanced data (50% normal, 50% attacks)
3. ✅ Deploy model automatically
4. ✅ Restart services

## Manual Steps

### 1. Download Datasets
```bash
./download_datasets.sh
```

### 2. Train Model
```bash
python3 train_comprehensive.py
```

### 3. Deploy
```bash
docker cp models/anomaly_detector.pkl hids_ml_service:/app/models/
docker cp models/scaler.pkl hids_ml_service:/app/models/
docker cp models/model_type.txt hids_ml_service:/app/models/
docker compose restart ml_service hids_engine
```

## What Gets Downloaded

```
hids/datasets/
├── KDDTrain+.txt                    # NSL-KDD training
├── KDDTest+.txt                     # NSL-KDD testing
├── Friday-*.csv                     # CICIDS2017 files
├── Thursday-*.csv                   # CICIDS2018 files
└── UNSW-NB15.csv                    # UNSW dataset
```

## Training Details

### Dataset Composition
```
NSL-KDD:      125,973 samples (67% normal)
CICIDS2017:   100,000 samples (20% normal)
CICIDS2018:    50,000 samples (15% normal)
─────────────────────────────────────────
Total:        275,973 samples

After Balancing:
Normal:        50,000 samples (50%)
Attack:        50,000 samples (50%)
─────────────────────────────────────────
Final:        100,000 samples (BALANCED)
```

### Why This Works Better

**Old Model:**
- Trained on: CICIDS2017 only (80% attacks)
- Normal traffic: Limited to CICIDS2017 baseline
- Result: 97% anomaly rate (everything looks like attack)

**New Model:**
- Trained on: NSL-KDD + CICIDS2017 + CICIDS2018
- Normal traffic: Rich baseline from NSL-KDD (67% normal)
- Balanced: 50/50 split
- Result: 5-15% anomaly rate (accurate detection)

## Troubleshooting

### Error: "401 Unauthorized"
```bash
# Kaggle credentials not set up
# Follow "Setup Kaggle API" steps above
```

### Error: "Dataset not found"
```bash
# Check dataset names on Kaggle
kaggle datasets list -s "nslkdd"
kaggle datasets list -s "cicids"
```

### Error: "Out of memory"
```bash
# Reduce sample size in train_comprehensive.py
# Line: .sample(50000, random_state=42)
# Change to: .sample(20000, random_state=42)
```

### Slow Download
```bash
# Download specific datasets only
cd datasets
kaggle datasets download -d hassan06/nslkdd
kaggle datasets download -d cicdataset/cicids2017
unzip "*.zip"
```

## Expected Results

### Before (Old Model)
```
Training Data: CICIDS2017 only
Normal Traffic: 20% (limited baseline)
Anomaly Rate: 97%
False Positives: Very High
```

### After (New Model)
```
Training Data: NSL-KDD + CICIDS2017 + CICIDS2018
Normal Traffic: 50% (rich baseline from NSL-KDD)
Anomaly Rate: 5-15%
False Positives: <5%
```

## Verification

```bash
# 1. Check model type
docker exec hids_ml_service cat /app/models/model_type.txt
# Should show: random_forest_comprehensive

# 2. Test system
python3 test_mvp.py

# 3. Check dashboard
# Visit: http://localhost:5000
# Anomaly rate should be 5-15%
```

## Alternative: Direct Kaggle Links

If scripts don't work, download manually:

1. **NSL-KDD**: https://www.kaggle.com/datasets/hassan06/nslkdd
2. **CICIDS2017**: https://www.kaggle.com/datasets/cicdataset/cicids2017
3. **CICIDS2018**: https://www.kaggle.com/datasets/solarmainframe/ids-intrusion-csv

Extract to: `/home/ghost/Desktop/TeralinkxV3/hids/datasets/`

## Time Estimates

- Download datasets: 10-30 minutes (depends on internet)
- Training: 5-15 minutes (depends on CPU)
- Deployment: 1 minute
- **Total: ~20-45 minutes**

## Summary

This approach gives you:
- ✅ **Rich normal traffic baseline** (NSL-KDD has 67% normal)
- ✅ **Diverse attack patterns** (3 different datasets)
- ✅ **Balanced training** (50/50 split)
- ✅ **Low false positives** (<5% target)
- ✅ **Production ready** (5-15% anomaly rate)
