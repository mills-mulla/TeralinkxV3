#!/usr/bin/env python3
# test_unified_payment.py
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8009"
TEST_TOKEN = "your_jwt_token_here"  # You'll need to get this from login

def test_unified_payment():
    """Test the unified payment endpoint"""
    
    # Test data
    test_data = {
        "payment_method": "credit",
        "package_id": 3,  # Assuming package ID 3 exists
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEST_TOKEN}"
    }
    
    try:
        # Test unified payment endpoint
        response = requests.post(
            f"{BASE_URL}/api/payments/unified/",
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Unified payment endpoint is working!")
        else:
            print("❌ Unified payment endpoint has issues")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_endpoint_availability():
    """Test if the endpoint is available"""
    try:
        # Test without authentication first
        response = requests.post(
            f"{BASE_URL}/api/payments/unified/",
            json={"test": "data"},
            timeout=5
        )
        
        print(f"Endpoint Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint is available (requires authentication)")
        elif response.status_code == 404:
            print("❌ Endpoint not found - check URL configuration")
        else:
            print(f"Endpoint responded with: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot reach endpoint: {e}")

if __name__ == "__main__":
    print("Testing Unified Payment System...")
    print("=" * 50)
    
    print("\n1. Testing endpoint availability...")
    test_endpoint_availability()
    
    print("\n2. Testing with authentication (requires valid token)...")
    # test_unified_payment()  # Uncomment when you have a valid token
    
    print("\nTest completed!")