import socket
import subprocess
import re
import os
import platform
from django.conf import settings
from ipware import get_client_ip

class NetworkUtils:
    
    @staticmethod
    def get_client_ip(request):
        """
        Get the real client IP address from request
        Returns: (ip_address, is_routable)
        """
        ip, is_routable = get_client_ip(request)
        return ip
    
    @staticmethod
    def get_mac_from_ip(ip_address):
        """
        Attempt to get MAC address from IP using system ARP table
        Works on Linux, macOS, and Windows
        """
        if not ip_address:
            return None
            
        # Get system platform
        system_platform = platform.system().lower()
        
        try:
            if system_platform == 'linux':
                return NetworkUtils._get_mac_linux(ip_address)
            elif system_platform == 'darwin':  # macOS
                return NetworkUtils._get_mac_macos(ip_address)
            elif system_platform == 'windows':
                return NetworkUtils._get_mac_windows(ip_address)
            else:
                return NetworkUtils._get_mac_generic(ip_address)
        except Exception as e:
            print(f"MAC detection error for {ip_address}: {e}")
            return None
    
    @staticmethod
    def _get_mac_linux(ip_address):
        """Get MAC address on Linux systems"""
        try:
            # Method 1: Read /proc/net/arp
            with open('/proc/net/arp', 'r') as f:
                lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 4 and parts[0] == ip_address:
                        mac = parts[3]
                        if mac != '00:00:00:00:00:00':
                            return mac.upper()
            
            # Method 2: Use arp command
            try:
                arp_output = subprocess.check_output(
                    ['arp', '-n', ip_address],
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                mac_pattern = r'(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))'
                match = re.search(mac_pattern, arp_output)
                if match:
                    return match.group(1).upper()
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
                
        except Exception as e:
            print(f"Linux MAC detection failed: {e}")
            
        return None
    
    @staticmethod
    def _get_mac_macos(ip_address):
        """Get MAC address on macOS"""
        try:
            # macOS arp command
            arp_output = subprocess.check_output(
                ['arp', '-n', ip_address],
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            # macOS arp output format: ? (192.168.1.1) at ab:cd:ef:12:34:56 on en0
            mac_pattern = r'at\s+(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))'
            match = re.search(mac_pattern, arp_output)
            if match:
                return match.group(1).upper()
                
        except Exception as e:
            print(f"macOS MAC detection failed: {e}")
            
        return None
    
    @staticmethod
    def _get_mac_windows(ip_address):
        """Get MAC address on Windows"""
        try:
            # Windows arp command
            arp_output = subprocess.check_output(
                ['arp', '-a', ip_address],
                stderr=subprocess.DEVNULL,
                text=True,
                shell=True  # Needed for Windows
            )
            
            # Windows arp output format
            mac_pattern = r'(([0-9A-Fa-f]{2}-){5}([0-9A-Fa-f]{2}))'
            match = re.search(mac_pattern, arp_output)
            if match:
                # Convert Windows format (dashes) to standard format (colons)
                mac = match.group(1).upper().replace('-', ':')
                return mac
                
        except Exception as e:
            print(f"Windows MAC detection failed: {e}")
            
        return None
    
    @staticmethod
    def _get_mac_generic(ip_address):
        """Generic MAC address detection"""
        try:
            # Try to ping the IP first to populate ARP cache
            if platform.system().lower() == 'windows':
                subprocess.run(['ping', '-n', '1', '-w', '1000', ip_address], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            else:
                subprocess.run(['ping', '-c', '1', '-W', '1', ip_address], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            
            # Try arp command with generic approach
            arp_output = subprocess.check_output(
                ['arp', '-a'],
                stderr=subprocess.DEVNULL,
                text=True
            )
            
            # Search for IP in ARP output
            lines = arp_output.split('\n')
            for line in lines:
                if ip_address in line:
                    # Try different MAC address patterns
                    patterns = [
                        r'(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))',
                        r'(([0-9A-Fa-f]{2}-){5}([0-9A-Fa-f]{2}))'
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, line)
                        if match:
                            mac = match.group(1).upper()
                            # Normalize to colon format
                            mac = mac.replace('-', ':')
                            return mac
                            
        except Exception as e:
            print(f"Generic MAC detection failed: {e}")
            
        return None
    
    @staticmethod
    def get_mac_from_dhcp(ip_address):
        """
        Alternative: Get MAC from DHCP server logs
        This requires access to DHCP server logs
        """
        dhcp_log_paths = [
            '/var/log/dhcpd.log',  # ISC DHCP
            '/var/log/dhcp.log',
            '/var/log/messages',
            '/var/log/syslog'
        ]
        
        for log_path in dhcp_log_paths:
            if os.path.exists(log_path):
                try:
                    with open(log_path, 'r') as f:
                        # Read last 1000 lines (recent entries)
                        lines = f.readlines()[-1000:]
                        
                        # Search for IP in recent DHCP entries
                        for line in reversed(lines):
                            if ip_address in line:
                                # Look for MAC address pattern
                                mac_pattern = r'(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))'
                                match = re.search(mac_pattern, line)
                                if match:
                                    return match.group(1).upper()
                except Exception as e:
                    continue
                    
        return None
    
    @staticmethod
    def get_hotspot_info(request):
        """
        Extract hotspot information from request
        """
        hotspot_info = {
            'name': None,
            'location_id': None,
            'ssid': None,
            'bssid': None,
            'gateway_ip': None
        }
        
        # Check headers commonly set by hotspot gateways
        hotspot_headers = {
            'X-Hotspot-Name': 'name',
            'X-Hotspot-Location-ID': 'location_id',
            'X-Hotspot-SSID': 'ssid',
            'X-Hotspot-BSSID': 'bssid',
            'X-Hotspot-Gateway-IP': 'gateway_ip',
            'X-Mikrotik-Hotspot': 'name',
            'X-Ubiquiti-Hotspot': 'name',
            'X-CoovaChilli-Hotspot': 'name'
        }
        
        for header, field in hotspot_headers.items():
            value = request.headers.get(header)
            if value and not hotspot_info[field]:
                hotspot_info[field] = value
        
        # Check URL parameters
        if not hotspot_info['name']:
            hotspot_info['name'] = request.GET.get('hotspot') or request.GET.get('hs')
        
        # Check session for previously detected hotspot
        if not hotspot_info['name'] and hasattr(request, 'session'):
            hotspot_info['name'] = request.session.get('hotspot_name')
        
        # Try to detect from IP subnet
        if not hotspot_info['name']:
            client_ip = NetworkUtils.get_client_ip(request)
            if client_ip:
                hotspot_info['name'] = NetworkUtils._detect_hotspot_from_ip(client_ip)
        
        # Set default if still None
        if not hotspot_info['name']:
            hotspot_info['name'] = 'Teralinkx Hotspot'
            
        return hotspot_info
    
    @staticmethod
    def _detect_hotspot_from_ip(ip_address):
        """
        Detect hotspot based on IP address range
        Configure HOTSPOT_IP_RANGES in settings.py
        """
        if not ip_address:
            return None
            
        hotspot_ranges = getattr(settings, 'HOTSPOT_IP_RANGES', {})
        
        def ip_to_int(ip):
            try:
                parts = list(map(int, ip.split('.')))
                return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
            except:
                return 0
        
        try:
            ip_int = ip_to_int(ip_address)
            
            for hotspot_name, ip_range in hotspot_ranges.items():
                if isinstance(ip_range, list) and len(ip_range) == 2:
                    start_ip = ip_to_int(ip_range[0])
                    end_ip = ip_to_int(ip_range[1])
                    if start_ip <= ip_int <= end_ip:
                        return hotspot_name
                elif isinstance(ip_range, str):
                    # Check if IP matches subnet (e.g., "192.168.1.0/24")
                    if '/' in ip_range:
                        network_ip, prefix = ip_range.split('/')
                        prefix = int(prefix)
                        network_int = ip_to_int(network_ip)
                        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
                        if (ip_int & mask) == (network_int & mask):
                            return hotspot_name
                        
        except Exception as e:
            print(f"Hotspot IP detection error: {e}")
            
        return None
    
    @staticmethod
    def get_gateway_ip():
        """
        Get default gateway IP address
        """
        try:
            if platform.system().lower() == 'windows':
                # Windows: Get default gateway
                output = subprocess.check_output(
                    ['route', 'print', '0.0.0.0'],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    shell=True
                )
                # Parse gateway from route print output
                lines = output.split('\n')
                for line in lines:
                    if '0.0.0.0' in line and 'On-link' not in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
            else:
                # Linux/macOS: Get default gateway
                output = subprocess.check_output(
                    ['ip', 'route', 'show', 'default'],
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                # Output: default via 192.168.1.1 dev eth0
                match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', output)
                if match:
                    return match.group(1)
                    
                # Alternative: netstat
                output = subprocess.check_output(
                    ['netstat', '-rn'],
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                lines = output.split('\n')
                for line in lines:
                    if 'default' in line or '0.0.0.0' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1]
                            
        except Exception as e:
            print(f"Gateway IP detection failed: {e}")
            
        return '192.168.1.1'  # Default fallback
    
    @staticmethod
    def validate_hotspot_access(client_ip, hotspot_name):
        """
        Validate if client IP is allowed to access this hotspot
        Can be used for location-based access control
        """
        # Get allowed IP ranges for this hotspot
        hotspot_ranges = getattr(settings, 'HOTSPOT_ACCESS_RULES', {}).get(hotspot_name, [])
        
        if not hotspot_ranges:  # No restrictions
            return True
            
        def ip_to_int(ip):
            try:
                parts = list(map(int, ip.split('.')))
                return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
            except:
                return 0
        
        ip_int = ip_to_int(client_ip)
        
        for ip_range in hotspot_ranges:
            if isinstance(ip_range, list) and len(ip_range) == 2:
                start_ip = ip_to_int(ip_range[0])
                end_ip = ip_to_int(ip_range[1])
                if start_ip <= ip_int <= end_ip:
                    return True
            elif isinstance(ip_range, str):
                # Check subnet
                if '/' in ip_range:
                    network_ip, prefix = ip_range.split('/')
                    prefix = int(prefix)
                    network_int = ip_to_int(network_ip)
                    mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
                    if (ip_int & mask) == (network_int & mask):
                        return True
                        
        return False