#!/usr/bin/env python3
import requests
import time
import sys

BASE_URL_DASHBOARD = "http://localhost:5002"
BASE_URL_ML = "http://localhost:5001"

def test_dashboard():
    """Test dashboard endpoints"""
    print("\n=== Testing Dashboard ===")
    
    endpoints = [
        "/",
        "/stats",
        "/alerts?limit=5",
        "/alerts/recent",
        "/top-sources?limit=5",
        "/top-destinations?limit=5",
        "/correlated"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL_DASHBOARD}{endpoint}", timeout=5)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} GET {endpoint} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Response keys: {list(data.keys())}")
        except Exception as e:
            print(f"✗ GET {endpoint} - Error: {e}")

def test_ml_service():
    """Test ML service endpoints"""
    print("\n=== Testing ML Service ===")
    
    # Health check
    try:
        response = requests.get(f"{BASE_URL_ML}/health", timeout=5)
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} GET /health - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"✗ GET /health - Error: {e}")
    
    # Prediction test
    try:
        test_features = {
            "features": [80, 443, 1.5, 1024, 2048, 10, 1, 1]
        }
        response = requests.post(
            f"{BASE_URL_ML}/predict",
            json=test_features,
            timeout=5
        )
        status = "✓" if response.status_code == 200 else "✗"
        print(f"{status} POST /predict - Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Prediction: {response.json()}")
    except Exception as e:
        print(f"✗ POST /predict - Error: {e}")

def test_database_connection():
    """Test if alerts are being stored"""
    print("\n=== Testing Database Storage ===")
    
    try:
        response = requests.get(f"{BASE_URL_DASHBOARD}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ Total alerts in database: {stats.get('total_alerts', 0)}")
            print(f"✓ Total connections: {stats.get('total_connections', 0)}")
            print(f"✓ Recent alerts (24h): {stats.get('recent_alerts_24h', 0)}")
            print(f"✓ Alerts by severity: {stats.get('alerts_by_severity', {})}")
        else:
            print(f"✗ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"✗ Database test failed: {e}")

def main():
    print("=" * 50)
    print("HIDS Stack Integration Tests")
    print("=" * 50)
    
    print("\nWaiting for services to be ready...")
    time.sleep(2)
    
    test_dashboard()
    test_ml_service()
    test_database_connection()
    
    print("\n" + "=" * 50)
    print("Tests completed!")
    print("=" * 50)

if __name__ == '__main__':
    main()
