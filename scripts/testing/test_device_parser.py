#!/usr/bin/env python3
# Test script for device parsing

import sys
import os
sys.path.append('/home/teralinkx/TeralinkxV3/teralinkx')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teralinkx.settings')

import django
django.setup()

from apps.core.utils.device_parser import DeviceParser

def test_nokia_device():
    """Test parsing your Nokia device User-Agent"""
    user_agent = "Mozilla/5.0 (Linux; Android 10; Nokia 3.1 Plus Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36"
    
    print("🔍 PARSING NOKIA DEVICE USER-AGENT")
    print("=" * 50)
    print(f"User-Agent: {user_agent}")
    print("=" * 50)
    
    device_info = DeviceParser.parse_user_agent(user_agent)
    
    print("📱 EXTRACTED DEVICE INFORMATION:")
    print(f"Device Type: {device_info['device_type']}")
    print(f"Manufacturer: {device_info['manufacturer']}")
    print(f"Model: {device_info['model']}")
    print(f"Platform: {device_info['platform']}")
    print(f"OS: {device_info['os_info']['full_name']}")
    print(f"Browser: {device_info['browser_info']['full_name']}")
    print()
    
    print("🏷️ GENERATED DEVICE NAME:")
    device_name = DeviceParser.generate_device_name(device_info, 'User_7999')
    print(f"Device Name: {device_name}")
    print()
    
    print("📋 DETAILED DEVICE INFO:")
    print(f"Raw Device String: {device_info['device_details']['raw_device_string']}")
    print(f"Build Info: {device_info['device_details']['build_info']}")
    print()
    
    print("🆚 BEFORE vs AFTER:")
    print(f"Before: User_7999's Desktop (A4:02:B9:8B:9B:3D)")
    print(f"After:  {device_name} (A4:02:B9:8B:9B:3D)")
    print()
    
    return device_info

if __name__ == "__main__":
    test_nokia_device()