from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import hashlib
import json
import time
from django.conf import settings
from core.utils.network_utils import NetworkUtils

class NetworkInfoView(APIView):
    """
    API endpoint to get client's network information
    This should be called before authentication to gather real network data
    """
    permission_classes = [AllowAny]
    
    def options(self, request, *args, **kwargs):
        """
        Handle OPTIONS preflight requests with proper CORS headers
        """
        response = Response({
            'status': 'preflight_ok',
            'message': 'CORS preflight successful',
            'allowed_methods': ['GET', 'OPTIONS'],
            'allowed_headers': [
                'accept',
                'content-type',
                'authorization',
                'x-session-id',
                'x-client-timestamp',
                'x-client-version',
                'x-hotspot-name'
            ]
        })
        
        # Get the origin from request
        origin = request.headers.get('Origin')
        
        # Set CORS headers
        if origin:
            response['Access-Control-Allow-Origin'] = origin
        else:
            response['Access-Control-Allow-Origin'] = '*'
        
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = ', '.join([
            'accept',
            'accept-encoding',
            'authorization', 
            'content-type',
            'dnt',
            'origin',
            'user-agent',
            'x-csrftoken',
            'x-requested-with',
            'x-session-id',
            'x-client-timestamp',
            'x-client-version',
            'x-hotspot-name'
        ])
        response['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        return response
    
    # Cache for 30 seconds to prevent abuse
    @method_decorator(cache_page(30))
    def get(self, request):
        """
        Get client's network information
        """
        try:
            # Generate a cache key based on request fingerprint
            cache_key = self._generate_cache_key(request)
            cached_response = cache.get(cache_key)
            
            if cached_response:
                response = Response(cached_response)
            else:
                # Get client IP with fallback
                client_ip = self._get_client_ip_safe(request)
                
                # Get MAC address (server-side detection) - only if we have valid IP
                client_mac = None
                if client_ip and client_ip != 'unknown':
                    try:
                        client_mac = NetworkUtils.get_mac_from_ip(client_ip)
                    except Exception as mac_error:
                        print(f"MAC detection failed for {client_ip}: {mac_error}")
                        client_mac = None
                
                # Get hotspot information
                hotspot_info = self._get_hotspot_info_safe(request)
                
                # Get device information safely
                device_info = self._get_device_info_safe(request)
                
                # Create session fingerprint
                session_fingerprint = self._create_session_fingerprint(
                    client_ip, client_mac, request
                )
                
                response_data = {
                    'ip': client_ip,
                    'mac': client_mac,
                    'hotspot_name': hotspot_info.get('name', 'Teralinkx Hotspot'),
                    'hotspot_location_id': hotspot_info.get('location_id'),
                    'hotspot_ssid': hotspot_info.get('ssid'),
                    'hotspot_bssid': hotspot_info.get('bssid'),
                    'device_info': device_info,
                    'session_fingerprint': session_fingerprint,
                    'timestamp': self._get_current_timestamp(),
                    'network_status': 'connected' if client_ip and client_ip != 'unknown' else 'scanning',
                    'requires_hotspot': True,
                    'is_captive_portal': self._is_captive_portal_request(request),
                    'detection_method': 'server_side'
                }
                
                # Cache the response only if we have valid IP
                if client_ip and client_ip != 'unknown':
                    cache.set(cache_key, response_data, 30)
                
                # Log the network info request
                self._log_network_request(request, response_data)
                
                response = Response(response_data, status=status.HTTP_200_OK)
            
            # Add CORS headers to GET response
            origin = request.headers.get('Origin')
            if origin:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Expose-Headers'] = 'x-session-id, x-client-version'
            
            return response
            
        except Exception as e:
            print(f"Network info error: {str(e)}")
            # Fallback response with better error information
            error_response = {
                'ip': self._get_fallback_ip(request),
                'mac': None,
                'hotspot_name': self._get_hotspot_name_from_request(request),
                'error': 'Network detection in progress',
                'requires_manual_entry': False,
                'timestamp': self._get_current_timestamp(),
                'network_status': 'scanning',
                'detection_method': 'fallback'
            }
            
            response = Response(error_response, status=status.HTTP_200_OK)
            
            # Add CORS headers to error response
            origin = request.headers.get('Origin')
            if origin:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
            
            return response
    
    def _get_hotspot_info_safe(self, request):
        """Safely get hotspot information with fallback"""
        try:
            # Check if NetworkUtils has get_hotspot_info method
            if hasattr(NetworkUtils, 'get_hotspot_info'):
                return NetworkUtils.get_hotspot_info(request)
            else:
                # Fallback implementation
                return self._get_hotspot_info_fallback(request)
        except Exception as e:
            print(f"Hotspot info error: {str(e)}")
            return self._get_hotspot_info_fallback(request)
    
    def _get_hotspot_info_fallback(self, request):
        """Fallback hotspot information extraction"""
        hotspot_info = {
            'name': 'Teralinkx Hotspot',
            'location_id': None,
            'ssid': None,
            'bssid': None
        }
        
        # Check headers
        hotspot_headers = {
            'X-Hotspot-Name': 'name',
            'X-Hotspot-Location-ID': 'location_id',
            'X-Hotspot-SSID': 'ssid',
            'X-Hotspot-BSSID': 'bssid',
        }
        
        for header, field in hotspot_headers.items():
            value = request.headers.get(header)
            if value:
                hotspot_info[field] = value
        
        # Check URL parameters
        if not hotspot_info['name'] or hotspot_info['name'] == 'Teralinkx Hotspot':
            hotspot_info['name'] = request.GET.get('hotspot') or request.GET.get('hs') or 'Teralinkx Hotspot'
        
        return hotspot_info
    
    def _get_device_info_safe(self, request):
        """Safely get device information"""
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        device_info = {
            'user_agent': user_agent,
            'is_mobile': False,
            'is_tablet': False,
            'is_desktop': False,
            'os': 'unknown',
            'browser': 'unknown',
            'device_type': 'unknown'
        }
        
        if not user_agent:
            return device_info
        
        # Simple device detection
        ua_lower = user_agent.lower()
        
        # Mobile detection
        mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'windows phone']
        tablet_keywords = ['ipad', 'tablet', 'kindle', 'silk', 'playbook']
        
        if any(keyword in ua_lower for keyword in tablet_keywords):
            device_info['is_tablet'] = True
            device_info['device_type'] = 'tablet'
        elif any(keyword in ua_lower for keyword in mobile_keywords):
            device_info['is_mobile'] = True
            device_info['device_type'] = 'mobile'
        else:
            device_info['is_desktop'] = True
            device_info['device_type'] = 'desktop'
        
        # OS detection
        if 'windows' in ua_lower:
            device_info['os'] = 'Windows'
        elif 'mac os x' in ua_lower or 'macintosh' in ua_lower:
            device_info['os'] = 'macOS'
        elif 'android' in ua_lower:
            device_info['os'] = 'Android'
        elif 'ios' in ua_lower or 'iphone' in ua_lower or 'ipad' in ua_lower:
            device_info['os'] = 'iOS'
        elif 'linux' in ua_lower:
            device_info['os'] = 'Linux'
        elif 'chrome os' in ua_lower:
            device_info['os'] = 'Chrome OS'
        
        # Browser detection
        if 'chrome' in ua_lower and 'edg' not in ua_lower and 'opr' not in ua_lower:
            device_info['browser'] = 'Chrome'
        elif 'firefox' in ua_lower:
            device_info['browser'] = 'Firefox'
        elif 'safari' in ua_lower and 'chrome' not in ua_lower:
            device_info['browser'] = 'Safari'
        elif 'edg' in ua_lower:
            device_info['browser'] = 'Edge'
        elif 'opera' in ua_lower or 'opr' in ua_lower:
            device_info['browser'] = 'Opera'
        elif 'trident' in ua_lower or 'msie' in ua_lower:
            device_info['browser'] = 'Internet Explorer'
        
        return device_info
    
    def _get_client_ip_safe(self, request):
        """Safe method to get client IP with multiple fallbacks"""
        try:
            # Try NetworkUtils first if it has the method
            if hasattr(NetworkUtils, 'get_client_ip'):
                ip = NetworkUtils.get_client_ip(request)
                if ip:
                    return ip
            
            # Fallback 1: X-Forwarded-For (common with proxies/load balancers)
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_list = x_forwarded_for.split(',')
                for ip_candidate in ip_list:
                    ip_candidate = ip_candidate.strip()
                    if self._is_valid_ip(ip_candidate):
                        return ip_candidate
            
            # Fallback 2: Standard REMOTE_ADDR
            remote_addr = request.META.get('REMOTE_ADDR')
            if remote_addr and self._is_valid_ip(remote_addr):
                return remote_addr
            
            # Fallback 3: Check various proxy headers
            proxy_headers = [
                'HTTP_X_REAL_IP',
                'HTTP_X_FORWARDED_HOST',
                'HTTP_CLIENT_IP',
                'HTTP_X_CLIENT_IP',
                'HTTP_X_CLUSTER_CLIENT_IP',
            ]
            
            for header in proxy_headers:
                ip_candidate = request.META.get(header)
                if ip_candidate and self._is_valid_ip(ip_candidate):
                    return ip_candidate
            
            # Fallback 4: Check if IP is in GET parameters (some hotspots)
            ip_param = request.GET.get('ip') or request.GET.get('client_ip')
            if ip_param and self._is_valid_ip(ip_param):
                return ip_param
            
            return 'unknown'
            
        except Exception as e:
            print(f"IP detection error: {str(e)}")
            return 'unknown'
    
    def _get_fallback_ip(self, request):
        """Get IP from various fallback sources"""
        # Try to get IP from REMOTE_ADDR first
        remote_addr = request.META.get('REMOTE_ADDR')
        if remote_addr and self._is_valid_ip(remote_addr):
            return remote_addr
        
        # Check X-Forwarded-For
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_candidate = x_forwarded_for.split(',')[0].strip()
            if self._is_valid_ip(ip_candidate):
                return ip_candidate
        
        # Default hotspot IP pattern
        return '10.10.21.131'
    
    def _get_hotspot_name_from_request(self, request):
        """Extract hotspot name from request"""
        # Check headers first
        hotspot_headers = [
            'HTTP_X_HOTSPOT_NAME',
            'HTTP_X_HOTSPOT',
            'HTTP_X_UBIQUITI_HOTSPOT',
            'HTTP_X_MIKROTIK_HOTSPOT',
            'X-Hotspot-Name',
            'X-Hotspot',
        ]
        
        for header in hotspot_headers:
            if header.startswith('HTTP_'):
                name = request.META.get(header)
            else:
                name = request.headers.get(header)
            
            if name:
                return name
        
        # Check URL parameters
        hotspot = request.GET.get('hotspot') or request.GET.get('hs')
        if hotspot:
            return hotspot
        
        # Default name
        return 'Teralinkx Hotspot'
    
    def _is_valid_ip(self, ip):
        """Validate IP address format"""
        if not ip or ip.lower() in ['unknown', 'none', 'null', '']:
            return False
        
        try:
            # Check IPv4 format
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            for part in parts:
                if not part.isdigit():
                    return False
                num = int(part)
                if num < 0 or num > 255:
                    return False
            
            # Check for common invalid/loopback IPs
            invalid_ips = [
                '0.0.0.0',
                '255.255.255.255',
                '127.0.0.1',
                'localhost',
                '::1',
                'fe80::1',
            ]
            
            if ip in invalid_ips:
                return False
            
            return True
        except Exception:
            return False
    
    def _generate_cache_key(self, request):
        """Generate cache key based on request fingerprint"""
        try:
            client_ip = self._get_client_ip_safe(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            fingerprint_data = {
                'ip': client_ip,
                'user_agent': user_agent[:50] if user_agent else 'no_ua',
                'path': request.path,
                'timestamp': int(time.time() / 30)  # Change every 30 seconds
            }
            fingerprint_json = json.dumps(fingerprint_data, sort_keys=True)
            return f"network_info_{hashlib.md5(fingerprint_json.encode()).hexdigest()}"
        except Exception:
            # Fallback cache key
            return f"network_info_fallback_{int(time.time() / 30)}"
    
    def _create_session_fingerprint(self, ip, mac, request):
        """Create a unique fingerprint for this session"""
        try:
            fingerprint_data = {
                'ip': ip or 'unknown',
                'mac': mac or 'unknown',
                'user_agent': (request.META.get('HTTP_USER_AGENT', '')[:100] 
                              if request.META.get('HTTP_USER_AGENT') else 'unknown'),
                'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', 'unknown'),
                'timestamp': int(time.time())
            }
            fingerprint_json = json.dumps(fingerprint_data, sort_keys=True)
            return hashlib.sha256(fingerprint_json.encode()).hexdigest()[:32]
        except Exception:
            return hashlib.sha256(str(time.time()).encode()).hexdigest()[:32]
    
    def _get_current_timestamp(self):
        """Get current timestamp in ISO format"""
        from django.utils import timezone
        return timezone.now().isoformat()
    
    def _is_captive_portal_request(self, request):
        """Check if this is likely a captive portal request"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Common captive portal detection patterns
        captive_indicators = [
            'captive',
            'hotspot',
            'wifi',
            'android-setup',
            'ios-setup',
            'mikrotik',
            'ubiquiti',
            'coovachilli',
            'wifidog',
            'nodogsplash'
        ]
        
        # Check headers that captive portals often set
        captive_headers = [
            'X-Hotspot',
            'X-Captive-Portal',
            'X-Mikrotik-Hotspot',
            'X-Ubiquiti-Hotspot',
            'X-CoovaChilli-Hotspot'
        ]
        
        # Check if any captive header exists
        for header in captive_headers:
            if header in request.headers:
                return True
        
        # Check User-Agent for captive portal clients
        if any(indicator in user_agent for indicator in captive_indicators):
            return True
            
        # Check referrer or origin
        referrer = request.META.get('HTTP_REFERER', '')
        if any(indicator in referrer.lower() for indicator in captive_indicators):
            return True
            
        # Check path - captive portals often have specific paths
        path = request.path.lower()
        if any(indicator in path for indicator in captive_indicators):
            return True
            
        return False
    
    def _log_network_request(self, request, network_data):
        """Log network requests for security auditing"""
        try:
            # Try to import and use the model if it exists
            from core.models.network_log import NetworkDetectionLog
            from django.utils import timezone
            
            NetworkDetectionLog.objects.create(
                client_ip=network_data['ip'],
                client_mac=network_data['mac'],
                hotspot_name=network_data['hotspot_name'],
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                session_fingerprint=network_data.get('session_fingerprint', ''),
                is_captive_portal=network_data.get('is_captive_portal', False),
                detected_at=timezone.now(),
                request_path=request.path,
                request_method=request.method
            )
        except Exception as e:
            # Just log to console if model doesn't exist
            print(f"Network request - IP: {network_data.get('ip')}, "
                  f"MAC: {network_data.get('mac')}, "
                  f"Hotspot: {network_data.get('hotspot_name')}")