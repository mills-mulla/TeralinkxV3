#!/usr/bin/env python3
import json
import time
from datetime import datetime
import random

# Sample alert signatures
SIGNATURES = [
    "ET SCAN Potential SSH Scan",
    "ET POLICY HTTP Request to a *.top domain",
    "ET MALWARE Suspicious User-Agent",
    "ET SCAN Potential Port Scan",
    "ET POLICY Suspicious inbound to MSSQL port 1433"
]

CATEGORIES = ["Attempted Information Leak", "Potentially Bad Traffic", "Misc Attack"]

def generate_alert():
    """Generate a sample Suricata alert"""
    return {
        "timestamp": datetime.now().isoformat(),
        "flow_id": random.randint(100000, 999999),
        "event_type": "alert",
        "src_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        "src_port": random.randint(1024, 65535),
        "dest_ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
        "dest_port": random.choice([22, 80, 443, 1433, 3306, 8080]),
        "proto": random.choice(["TCP", "UDP"]),
        "alert": {
            "signature": random.choice(SIGNATURES),
            "category": random.choice(CATEGORIES),
            "severity": random.randint(1, 3)
        }
    }

def main():
    print("Generating test alerts to /data/suricata/eve.json")
    
    with open('/data/suricata/eve.json', 'a') as f:
        for i in range(20):
            alert = generate_alert()
            f.write(json.dumps(alert) + '\n')
            f.flush()
            print(f"Generated alert {i+1}: {alert['alert']['signature']}")
            time.sleep(0.5)
    
    print("Test alerts generated successfully!")

if __name__ == '__main__':
    main()
