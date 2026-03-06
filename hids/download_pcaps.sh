#!/bin/bash
# Download CIC-IDS2017 PCAP files for HIDS testing

PCAP_DIR="./hids/pcaps"
mkdir -p "$PCAP_DIR"

echo "Downloading CIC-IDS2017 PCAP samples..."

# CIC-IDS2017 dataset URLs (sample files)
# Full dataset: https://www.unb.ca/cic/datasets/ids-2017.html

# Download smaller sample PCAPs for testing
wget -O "$PCAP_DIR/friday-workingHours.pcap" \
  "https://iscxdownloads.cs.unb.ca/iscxdownloads/CIC-IDS-2017/PCAPs/Friday-WorkingHours.pcap" \
  2>/dev/null || echo "Note: Full dataset requires registration at unb.ca/cic/datasets"

# Alternative: Use publicly available samples
echo "Downloading sample attack traffic..."
wget -O "$PCAP_DIR/ddos_sample.pcap" \
  "https://tcpreplay.appneta.com/wiki/captures/ddos.pcap" 2>/dev/null

wget -O "$PCAP_DIR/portscan_sample.pcap" \
  "https://tcpreplay.appneta.com/wiki/captures/portscan.pcap" 2>/dev/null

echo ""
echo "Available PCAP files:"
ls -lh "$PCAP_DIR"/*.pcap 2>/dev/null || echo "No PCAP files downloaded"

echo ""
echo "To replay traffic:"
echo "  docker run --rm --network host --cap-add=NET_ADMIN --cap-add=NET_RAW \\"
echo "    -v \$(pwd)/hids/pcaps:/pcaps teralinkxv3-tcpreplay \\"
echo "    tcpreplay -i wlp2s0 -t /pcaps/ddos_sample.pcap"
