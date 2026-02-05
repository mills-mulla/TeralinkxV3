# apps/core/utils/device_parser.py
import re
import json
from typing import Dict, Optional, Tuple
from django.http import HttpRequest

class DeviceParser:
    """Parse User-Agent and extract detailed device information"""
    
    # Device type patterns
    MOBILE_PATTERNS = [
        r'Mobile', r'Android', r'iPhone', r'iPad', r'iPod', r'BlackBerry', 
        r'Windows Phone', r'Opera Mini', r'IEMobile'
    ]
    
    TABLET_PATTERNS = [
        r'iPad', r'Android.*Tablet', r'Kindle', r'Silk/', r'PlayBook'
    ]
    
    TV_PATTERNS = [
        r'Smart-TV', r'SmartTV', r'GoogleTV', r'AppleTV', r'Roku', 
        r'WebOS', r'Tizen', r'NetCast', r'HbbTV'
    ]
    
    GAMING_PATTERNS = [
        r'PlayStation', r'Xbox', r'Nintendo', r'Steam'
    ]
    
    @staticmethod
    def parse_user_agent(user_agent: str) -> Dict:
        """Parse User-Agent string into structured data"""
        if not user_agent:
            return DeviceParser._get_default_info()
        
        # Extract basic info
        device_info = {
            'user_agent': user_agent,
            'device_type': DeviceParser._detect_device_type(user_agent),
            'os_info': DeviceParser._extract_os_info(user_agent),
            'browser_info': DeviceParser._extract_browser_info(user_agent),
            'device_details': DeviceParser._extract_device_details(user_agent),
            'manufacturer': DeviceParser._extract_manufacturer(user_agent),
            'model': DeviceParser._extract_model(user_agent),
            'platform': DeviceParser._extract_platform(user_agent)
        }
        
        return device_info
    
    @staticmethod
    def _detect_device_type(user_agent: str) -> str:
        """Detect device type from User-Agent"""
        ua_lower = user_agent.lower()
        
        # Check for TV first
        for pattern in DeviceParser.TV_PATTERNS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return 'smart_tv'
        
        # Check for gaming consoles
        for pattern in DeviceParser.GAMING_PATTERNS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return 'gaming_console'
        
        # Check for tablets (before mobile, as some tablets include "Mobile")
        for pattern in DeviceParser.TABLET_PATTERNS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return 'tablet'
        
        # Check for mobile
        for pattern in DeviceParser.MOBILE_PATTERNS:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return 'mobile'
        
        # Default to desktop
        return 'desktop'
    
    @staticmethod
    def _extract_os_info(user_agent: str) -> Dict:
        """Extract OS information"""
        os_patterns = {
            'Windows': r'Windows NT ([\d.]+)',
            'macOS': r'Mac OS X ([\d_]+)',
            'iOS': r'OS ([\d_]+)',
            'Android': r'Android ([\d.]+)',
            'Linux': r'Linux',
            'Chrome OS': r'CrOS'
        }
        
        for os_name, pattern in os_patterns.items():
            match = re.search(pattern, user_agent)
            if match:
                version = match.group(1) if match.groups() else 'Unknown'
                if os_name == 'macOS':
                    version = version.replace('_', '.')
                return {
                    'name': os_name,
                    'version': version,
                    'full_name': f"{os_name} {version}"
                }
        
        return {'name': 'Unknown', 'version': 'Unknown', 'full_name': 'Unknown OS'}
    
    @staticmethod
    def _extract_browser_info(user_agent: str) -> Dict:
        """Extract browser information"""
        browser_patterns = {
            'Chrome': r'Chrome/([\d.]+)',
            'Firefox': r'Firefox/([\d.]+)',
            'Safari': r'Version/([\d.]+).*Safari',
            'Edge': r'Edg/([\d.]+)',
            'Opera': r'OPR/([\d.]+)',
            'Samsung Browser': r'SamsungBrowser/([\d.]+)',
            'UC Browser': r'UCBrowser/([\d.]+)'
        }
        
        for browser_name, pattern in browser_patterns.items():
            match = re.search(pattern, user_agent)
            if match:
                version = match.group(1)
                return {
                    'name': browser_name,
                    'version': version,
                    'full_name': f"{browser_name} {version}"
                }
        
        return {'name': 'Unknown', 'version': 'Unknown', 'full_name': 'Unknown Browser'}
    
    @staticmethod
    def _extract_device_details(user_agent: str) -> Dict:
        """Extract specific device details"""
        # Android device pattern
        android_match = re.search(r'Android.*?;\s*([^)]+)\)', user_agent)
        if android_match:
            device_string = android_match.group(1).strip()
            # Parse device string like "Nokia 3.1 Plus Build/QP1A.190711.020"
            parts = device_string.split(' Build/')
            device_name = parts[0].strip()
            build_info = parts[1] if len(parts) > 1 else None
            
            return {
                'device_name': device_name,
                'build_info': build_info,
                'raw_device_string': device_string
            }
        
        # iPhone/iPad pattern
        ios_match = re.search(r'(iPhone|iPad|iPod).*?OS ([\d_]+)', user_agent)
        if ios_match:
            device_type = ios_match.group(1)
            os_version = ios_match.group(2).replace('_', '.')
            return {
                'device_name': device_type,
                'os_version': os_version,
                'raw_device_string': f"{device_type} iOS {os_version}"
            }
        
        return {'device_name': 'Unknown', 'build_info': None, 'raw_device_string': 'Unknown Device'}
    
    @staticmethod
    def _extract_manufacturer(user_agent: str) -> str:
        """Extract device manufacturer"""
        manufacturers = {
            'Samsung': r'Samsung|SM-|GT-',
            'Apple': r'iPhone|iPad|iPod|Macintosh',
            'Google': r'Pixel|Nexus',
            'Huawei': r'Huawei|HUAWEI',
            'Xiaomi': r'Xiaomi|Mi |Redmi',
            'OnePlus': r'OnePlus|ONEPLUS',
            'Sony': r'Sony|Xperia',
            'LG': r'LG-|LG |LGE',
            'HTC': r'HTC',
            'Motorola': r'Motorola|Moto',
            'Nokia': r'Nokia',
            'Oppo': r'OPPO',
            'Vivo': r'vivo',
            'Realme': r'RMX|Realme'
        }
        
        for manufacturer, pattern in manufacturers.items():
            if re.search(pattern, user_agent, re.IGNORECASE):
                return manufacturer
        
        return 'Unknown'
    
    @staticmethod
    def _extract_model(user_agent: str) -> str:
        """Extract device model"""
        # Android model extraction
        android_match = re.search(r'Android.*?;\s*([^)]+)\)', user_agent)
        if android_match:
            device_string = android_match.group(1).strip()
            # Remove build info
            model = device_string.split(' Build/')[0].strip()
            return model
        
        # iPhone model extraction
        iphone_match = re.search(r'iPhone.*?OS', user_agent)
        if iphone_match:
            return 'iPhone'
        
        # iPad model extraction
        ipad_match = re.search(r'iPad.*?OS', user_agent)
        if ipad_match:
            return 'iPad'
        
        return 'Unknown Model'
    
    @staticmethod
    def _extract_platform(user_agent: str) -> str:
        """Extract platform information"""
        if 'Android' in user_agent:
            android_match = re.search(r'Android ([\d.]+)', user_agent)
            version = android_match.group(1) if android_match else 'Unknown'
            return f"Android {version}"
        
        if 'iPhone' in user_agent or 'iPad' in user_agent:
            ios_match = re.search(r'OS ([\d_]+)', user_agent)
            version = ios_match.group(1).replace('_', '.') if ios_match else 'Unknown'
            return f"iOS {version}"
        
        if 'Windows NT' in user_agent:
            windows_match = re.search(r'Windows NT ([\d.]+)', user_agent)
            version = windows_match.group(1) if windows_match else 'Unknown'
            return f"Windows {version}"
        
        if 'Mac OS X' in user_agent:
            mac_match = re.search(r'Mac OS X ([\d_]+)', user_agent)
            version = mac_match.group(1).replace('_', '.') if mac_match else 'Unknown'
            return f"macOS {version}"
        
        if 'Linux' in user_agent:
            return 'Linux'
        
        return 'Unknown Platform'
    
    @staticmethod
    def _get_default_info() -> Dict:
        """Default device info when User-Agent is not available"""
        return {
            'user_agent': '',
            'device_type': 'unknown',
            'os_info': {'name': 'Unknown', 'version': 'Unknown', 'full_name': 'Unknown OS'},
            'browser_info': {'name': 'Unknown', 'version': 'Unknown', 'full_name': 'Unknown Browser'},
            'device_details': {'device_name': 'Unknown', 'build_info': None, 'raw_device_string': 'Unknown Device'},
            'manufacturer': 'Unknown',
            'model': 'Unknown Model',
            'platform': 'Unknown Platform'
        }
    
    @staticmethod
    def generate_device_name(device_info: Dict, user_name: str = "User") -> str:
        """Generate a user-friendly device name"""
        manufacturer = device_info.get('manufacturer', 'Unknown')
        model = device_info.get('model', 'Unknown Model')
        device_type = device_info.get('device_type', 'device')
        
        # Clean up model name
        if manufacturer != 'Unknown' and manufacturer.lower() not in model.lower():
            device_name = f"{manufacturer} {model}"
        else:
            device_name = model
        
        # Add device type if not obvious
        if device_type in ['smart_tv', 'gaming_console', 'tablet']:
            device_name += f" ({device_type.replace('_', ' ').title()})"
        
        return device_name
    
    @staticmethod
    def get_device_info_from_request(request: HttpRequest) -> Dict:
        """Extract complete device information from Django request"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Parse User-Agent
        device_info = DeviceParser.parse_user_agent(user_agent)
        
        # Add request-specific information
        device_info.update({
            'ip_address': DeviceParser._get_client_ip(request),
            'language': request.META.get('HTTP_ACCEPT_LANGUAGE', '').split(',')[0],
            'referer': request.META.get('HTTP_REFERER', ''),
            'timestamp': request.META.get('HTTP_DATE'),
        })
        
        return device_info
    
    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """Get real client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip
        
        return request.META.get('REMOTE_ADDR', '127.0.0.1')


# Example usage function
def parse_your_user_agent():
    """Example parsing your Nokia device"""
    user_agent = "Mozilla/5.0 (Linux; Android 10; Nokia 3.1 Plus Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36"
    
    device_info = DeviceParser.parse_user_agent(user_agent)
    
    print("Parsed Device Information:")
    print(f"Device Type: {device_info['device_type']}")
    print(f"Manufacturer: {device_info['manufacturer']}")
    print(f"Model: {device_info['model']}")
    print(f"Platform: {device_info['platform']}")
    print(f"OS: {device_info['os_info']['full_name']}")
    print(f"Browser: {device_info['browser_info']['full_name']}")
    print(f"Device Name: {DeviceParser.generate_device_name(device_info, 'User_7999')}")
    
    return device_info