#!/usr/bin/env python3
"""
FreeRADIUS API Test Script
Tests all endpoints: users, profiles, sessions, disconnect
"""

import requests
import json
import sys

BASE_URL = "http://192.168.88.16:8010/api"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

def test_profiles():
    """Test profile management"""
    print("\n🔵 TESTING PROFILES")
    
    # 1. Create profile with bandwidth only
    print("\n1️⃣ Creating profile '5mbps' (bandwidth only)...")
    response = requests.post(f"{BASE_URL}/profiles/", json={
        "name": "5mbps",
        "upload_limit": "5M",
        "download_limit": "2M"
    })
    print_response("CREATE PROFILE (5mbps)", response)
    
    # 2. Create profile with time limit
    print("\n2️⃣ Creating profile '1hour' (1 hour session timeout)...")
    response = requests.post(f"{BASE_URL}/profiles/", json={
        "name": "1hour",
        "upload_limit": "10M",
        "download_limit": "5M",
        "session_timeout": 3600  # 1 hour
    })
    print_response("CREATE PROFILE (1hour)", response)
    
    # 3. Create profile with data limit
    print("\n3️⃣ Creating profile '1gb' (1GB data limit)...")
    response = requests.post(f"{BASE_URL}/profiles/", json={
        "name": "1gb",
        "upload_limit": "8M",
        "download_limit": "3M",
        "data_limit": 1073741824  # 1GB in bytes
    })
    print_response("CREATE PROFILE (1gb)", response)
    
    # 4. List all profiles
    print("\n4️⃣ Listing all profiles...")
    response = requests.get(f"{BASE_URL}/profiles/")
    print_response("LIST PROFILES", response)
    
    # 5. Get specific profile
    print("\n5️⃣ Getting profile '5mbps'...")
    response = requests.get(f"{BASE_URL}/profiles/?name=5mbps")
    print_response("GET PROFILE (5mbps)", response)

def test_users():
    """Test user management"""
    print("\n🟢 TESTING USERS")
    
    # 1. Create user without profile
    print("\n1️⃣ Creating user 'testuser1' (no profile)...")
    response = requests.post(f"{BASE_URL}/users/", json={
        "username": "testuser1",
        "password": "password123"
    })
    print_response("CREATE USER (testuser1)", response)
    
    # 2. Create user with profile
    print("\n2️⃣ Creating user 'testuser2' (with 5mbps profile)...")
    response = requests.post(f"{BASE_URL}/users/", json={
        "username": "testuser2",
        "password": "password456",
        "profile": "5mbps"
    })
    print_response("CREATE USER (testuser2)", response)
    
    # 3. Create user with 1hour profile
    print("\n3️⃣ Creating user 'testuser3' (with 1hour profile)...")
    response = requests.post(f"{BASE_URL}/users/", json={
        "username": "testuser3",
        "password": "password789",
        "profile": "1hour"
    })
    print_response("CREATE USER (testuser3)", response)
    
    # 4. List all users
    print("\n4️⃣ Listing all users...")
    response = requests.get(f"{BASE_URL}/users/")
    print_response("LIST USERS", response)
    
    # 5. Get specific user
    print("\n5️⃣ Getting user 'testuser2'...")
    response = requests.get(f"{BASE_URL}/users/?username=testuser2")
    print_response("GET USER (testuser2)", response)

def test_sessions():
    """Test session viewing"""
    print("\n🟡 TESTING SESSIONS")
    
    # 1. List all active sessions
    print("\n1️⃣ Listing all active sessions...")
    response = requests.get(f"{BASE_URL}/sessions/")
    print_response("LIST SESSIONS", response)
    
    # 2. Get sessions for specific user
    print("\n2️⃣ Getting sessions for 'testuser'...")
    response = requests.get(f"{BASE_URL}/sessions/?username=testuser")
    print_response("GET USER SESSIONS", response)

def test_disconnect():
    """Test disconnect functionality"""
    print("\n🔴 TESTING DISCONNECT")
    
    # First check if there are active sessions
    print("\n1️⃣ Checking for active sessions...")
    response = requests.get(f"{BASE_URL}/sessions/")
    
    if response.status_code == 200:
        sessions = response.json().get('sessions', [])
        if sessions:
            session = sessions[0]
            username = session.get('username')
            session_id = session.get('acctsessionid')
            
            print(f"\n2️⃣ Disconnecting user '{username}' (session: {session_id})...")
            response = requests.post(f"{BASE_URL}/disconnect/", json={
                "username": username
            })
            print_response("DISCONNECT USER", response)
        else:
            print("\n⚠️  No active sessions found. Skipping disconnect test.")
            print("   To test disconnect:")
            print("   1. Connect a user via MikroTik PPPoE")
            print("   2. Run this test again")
    else:
        print_response("ERROR CHECKING SESSIONS", response)

def test_cleanup():
    """Clean up test data"""
    print("\n🧹 CLEANUP (Optional)")
    
    choice = input("\nDo you want to delete test users and profiles? (y/n): ")
    if choice.lower() != 'y':
        print("Skipping cleanup.")
        return
    
    # Delete users
    for username in ['testuser1', 'testuser2', 'testuser3']:
        print(f"\nDeleting user '{username}'...")
        response = requests.delete(f"{BASE_URL}/users/?username={username}")
        print(f"  Status: {response.status_code}")
    
    # Delete profiles
    for profile in ['5mbps', '1hour', '1gb']:
        print(f"\nDeleting profile '{profile}'...")
        response = requests.delete(f"{BASE_URL}/profiles/?name={profile}")
        print(f"  Status: {response.status_code}")
    
    print("\n✅ Cleanup complete!")

def main():
    """Run all tests"""
    print("="*60)
    print("FreeRADIUS API Test Suite")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print("="*60)
    
    try:
        # Test connection
        print("\n🔌 Testing API connection...")
        response = requests.get(f"{BASE_URL}/users/", timeout=5)
        print(f"✅ API is reachable (Status: {response.status_code})")
        
        # Run tests
        test_profiles()
        test_users()
        test_sessions()
        test_disconnect()
        test_cleanup()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to {BASE_URL}")
        print("   Make sure the API server is running:")
        print("   python manage.py runserver 0.0.0.0:8001")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
