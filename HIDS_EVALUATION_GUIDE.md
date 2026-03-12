# HIDS Evaluation & Testing Guide

## Overview
This guide explains how to evaluate the ML-powered HIDS using CICIDS2017 and CICIDS2018 PCAP files.

## Evaluation Dashboard Access
- **URL**: http://localhost:5002/evaluation
- **Features**: PCAP upload/replay, real-time metrics, confusion matrix, detection method comparison, zero-day detection analysis

---

## CICIDS2017 Dataset

### Attack Types & PCAP Files
1. **Monday (Benign)**: Normal traffic baseline
2. **Tuesday (Brute Force)**: FTP-Patator, SSH-Patator
3. **Wednesday (DoS/DDoS)**: DoS GoldenEye, DoS Hulk, DoS Slowhttptest, DoS slowloris, Heartbleed
4. **Thursday (Web Attacks)**: Web Attack - Brute Force, Web Attack - XSS, Web Attack - SQL Injection, Infiltration
5. **Friday (Botnet, PortScan, DDoS)**: Bot, PortScan, DDoS

### Download Sources
```bash
# Official UNB Source
wget https://www.unb.ca/cic/datasets/ids-2017.html

# Kaggle (requires account)
kaggle datasets download -d cicdataset/cicids2017

# Alternative: AWS S3 (if available)
aws s3 sync s3://cse-cic-ids2017/pcaps/ ./hids/pcaps/
```

---

## CICIDS2018 Dataset

### Attack Types & PCAP Files
1. **Wednesday-14-02**: Brute Force, FTP-Patator, SSH-Patator
2. **Thursday-15-02**: DoS attacks - Slowloris, Slowhttptest, Hulk, GoldenEye, Heartbleed
3. **Friday-16-02**: DDoS attacks - LOIC-HTTP, LOIC-UDP
4. **Wednesday-21-02**: Brute Force - XSS, SQL Injection
5. **Thursday-22-02**: Brute Force - XSS, SQL Injection, Infiltration
6. **Friday-23-02**: Botnet ARES, Port Scan, DDoS LOIC-UDP

### Download Sources
```bash
# Official UNB Source
wget https://www.unb.ca/cic/datasets/ids-2018.html

# Kaggle
kaggle datasets download -d solarmainframe/ids-intrusion-csv
```

---

## Evaluation Workflow

### Step 1: Upload PCAP Files
1. Navigate to http://localhost:5002/evaluation
2. Drag & drop PCAP file or click to browse
3. Upload file (stored in `/pcaps` directory)
4. Verify file appears in "Available PCAP Files" list

### Step 2: Configure Replay
- **Interface**: Select `br-c51890515ece` (Docker bridge network)
- **Speed**: Choose replay speed (1x = real-time, 10x = faster)
- **Note**: Higher speeds may cause packet loss

### Step 3: Start Replay
1. Select PCAP file from list
2. Click "▶️ Replay Selected"
3. Monitor detection timeline in real-time
4. Wait for replay to complete

### Step 4: Analyze Results
Monitor the following metrics:

#### Model Performance
- **Total Predictions**: Number of flows analyzed
- **Anomalies Detected**: Malicious traffic identified
- **Anomaly Rate**: Percentage of anomalous traffic
- **Avg Confidence**: ML model confidence (higher = better)

#### Detection Methods
- **ML Confirmed by Suricata**: Both systems agree (score 85-100)
- **ML Primary (Zero-Day)**: ML-only detection (score 60-85)
- **Suricata Override**: Signature-based only (score 40-60)
- **Both Normal**: Clean traffic (score 0-40)

#### Confusion Matrix (Requires Ground Truth)
- **TP (True Positive)**: Correctly identified attacks
- **TN (True Normal)**: Correctly identified normal traffic
- **FP (False Positive)**: Normal traffic flagged as attack
- **FN (False Negative)**: Missed attacks

#### Performance Metrics
- **Accuracy**: (TP + TN) / Total
- **Precision**: TP / (TP + FP) - How many detected attacks are real
- **Recall**: TP / (TP + FN) - How many real attacks were detected
- **F1-Score**: Harmonic mean of precision and recall
- **False Positive Rate**: FP / (FP + TN)

---

## Expected Results

### Baseline Model (Trained on Balanced Dataset)
- **Accuracy**: ~98%
- **False Positive Rate**: ~1.70%
- **Anomaly Rate**: 20-30% (on attack-heavy CICIDS2017 Friday)
- **Avg Confidence**: 85-95%

### Detection Method Distribution
- **ML Confirmed**: 40-50% (known attacks)
- **ML Primary**: 10-20% (zero-day/unknown patterns)
- **Suricata Override**: 5-10% (signature-based)
- **Both Normal**: 30-40% (clean traffic)

---

## Ground Truth Labeling

To calculate confusion matrix metrics, you need ground truth labels:

### Option 1: Use CICIDS CSV Labels
```python
import pandas as pd

# Load CICIDS2017 CSV with labels
df = pd.read_csv('Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv')

# Map labels to predictions
for index, row in df.iterrows():
    label = 'anomaly' if row['Label'] != 'BENIGN' else 'normal'
    # Update ml_predictions table with ground_truth
```

### Option 2: Manual Labeling
```sql
-- Label known attack IPs
UPDATE ml_predictions 
SET ground_truth = 'anomaly' 
WHERE features->>'src_ip' IN ('192.168.10.50', '192.168.10.51');

-- Label known benign IPs
UPDATE ml_predictions 
SET ground_truth = 'normal' 
WHERE features->>'src_ip' IN ('192.168.10.5', '192.168.10.8');
```

---

## Testing Scenarios

### Scenario 1: DDoS Attack Detection
**PCAP**: CICIDS2017 Friday (DDoS)
**Expected**: High anomaly rate (60-80%), ML Primary detections

### Scenario 2: Port Scan Detection
**PCAP**: CICIDS2017 Friday (PortScan)
**Expected**: Multiple connections from same source, repeated_attack alerts

### Scenario 3: Botnet Detection
**PCAP**: CICIDS2017 Friday (Bot) or CICIDS2018 Friday-23 (Botnet ARES)
**Expected**: ML Primary detections (zero-day), unusual traffic patterns

### Scenario 4: Web Attacks
**PCAP**: CICIDS2017 Thursday (XSS, SQL Injection)
**Expected**: Suricata Override or ML Confirmed, signature matches

### Scenario 5: Brute Force
**PCAP**: CICIDS2017 Tuesday (SSH-Patator, FTP-Patator)
**Expected**: Repeated connection attempts, high event_count

### Scenario 6: Normal Traffic Baseline
**PCAP**: CICIDS2017 Monday (Benign)
**Expected**: Low anomaly rate (<5%), Both Normal detections

---

## Performance Tuning

### Reduce False Positives
1. Increase ML confidence threshold in engine.py
2. Adjust composite score weights (currently 70% ML, 30% Suricata)
3. Retrain model with more normal traffic samples

### Improve Detection Rate
1. Update Suricata rules: `docker exec hids_suricata suricata-update`
2. Retrain ML model with more attack samples
3. Lower ML confidence threshold (increases FP rate)

### Optimize Speed
1. Increase replay speed (10x)
2. Reduce logging verbosity
3. Batch process predictions

---

## Export & Reporting

### Export Results
1. Click "💾 Export Results" button
2. Downloads JSON file with all detections
3. Includes timestamps, IPs, detection methods, scores

### Generate Report
```python
import json
import pandas as pd

# Load exported results
with open('hids_evaluation_1234567890.json') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data['results'])

# Generate statistics
print(f"Total Detections: {len(df)}")
print(f"By Severity: {df['severity'].value_counts()}")
print(f"By Detection Method: {df['metadata'].apply(lambda x: x.get('detection_method')).value_counts()}")
```

---

## Troubleshooting

### No Detections Appearing
- Check Suricata/Zeek logs: `docker logs hids_suricata`
- Verify interface: `docker exec hids_tcpreplay ip link show`
- Ensure HIDS engine is running: `docker logs hids_engine`

### High False Positive Rate
- Check model training data balance
- Review Suricata rules for outdated signatures
- Verify feature extraction is correct

### Low Detection Rate
- Update Suricata rules
- Retrain model with more diverse attack samples
- Check if PCAP contains actual attacks (use CICIDS CSV labels)

### Replay Not Working
- Verify tcpreplay container: `docker ps | grep tcpreplay`
- Check interface exists: `ip link show br-c51890515ece`
- Ensure PCAP file is valid: `tcpdump -r file.pcap -c 10`

---

## Best Practices

1. **Start with Benign Traffic**: Establish baseline with CICIDS2017 Monday
2. **Test One Attack Type at a Time**: Easier to analyze results
3. **Use Ground Truth Labels**: Required for confusion matrix
4. **Export Results**: Save for comparison after model updates
5. **Clear Test Data**: Between evaluations to avoid confusion
6. **Monitor Resource Usage**: Large PCAPs can consume significant memory
7. **Validate Results**: Cross-reference with CICIDS CSV labels

---

## Metrics Interpretation

### Anomaly Rate
- **<5%**: Normal traffic or model too conservative
- **5-20%**: Typical production environment
- **20-50%**: Attack-heavy traffic (expected for CICIDS)
- **>50%**: Possible model overfitting or misconfiguration

### ML Confidence
- **>90%**: High confidence, likely correct
- **70-90%**: Medium confidence, review manually
- **<70%**: Low confidence, may be false positive

### Detection Method
- **ML Confirmed**: Most reliable (both systems agree)
- **ML Primary**: Potential zero-day, investigate further
- **Suricata Override**: Known signature, but ML disagrees (review)
- **Both Normal**: Clean traffic

---

## Advanced Features

### Custom Attack Simulation
```bash
# Generate custom attack traffic
hping3 -S -p 80 --flood 192.168.1.100

# Replay at specific timestamp
tcpreplay -i br-c51890515ece -K --pps=1000 attack.pcap
```

### Real-time Monitoring
```bash
# Watch detections in real-time
watch -n 1 'curl -s http://localhost:5002/api/evaluation/model-performance | jq'

# Monitor Suricata alerts
tail -f hids/suricata/logs/eve.json | jq 'select(.event_type=="alert")'
```

### Batch Evaluation
```bash
# Evaluate all CICIDS2017 PCAPs
for pcap in hids/pcaps/CICIDS2017-*.pcap; do
    echo "Testing $pcap"
    curl -X POST http://localhost:5002/api/evaluation/replay-pcap \
         -H "Content-Type: application/json" \
         -d "{\"filename\": \"$(basename $pcap)\", \"speed\": 10}"
    sleep 300  # Wait 5 minutes
    curl http://localhost:5002/api/evaluation/export-results > "results_$(basename $pcap).json"
    curl -X POST http://localhost:5002/api/evaluation/clear-test-data
done
```

---

## References

- **CICIDS2017**: https://www.unb.ca/cic/datasets/ids-2017.html
- **CICIDS2018**: https://www.unb.ca/cic/datasets/ids-2018.html
- **Suricata Rules**: https://rules.emergingthreats.net/
- **ML Model Training**: See `/hids/train_memory_efficient.py`
- **Architecture**: See `HIDS_ARCHITECTURE.md`
