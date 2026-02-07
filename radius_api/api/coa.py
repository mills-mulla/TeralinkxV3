import socket
import struct
import hashlib
import secrets


class CoAClient:
    """RADIUS CoA (Change of Authorization) client for disconnecting users"""
    
    COA_REQUEST = 43
    COA_ACK = 44
    COA_NAK = 45
    DISCONNECT_REQUEST = 40
    DISCONNECT_ACK = 41
    DISCONNECT_NAK = 42
    
    def __init__(self, nas_ip, nas_secret, coa_port=3799, timeout=3):
        self.nas_ip = nas_ip
        self.nas_secret = nas_secret.encode() if isinstance(nas_secret, str) else nas_secret
        self.coa_port = coa_port
        self.timeout = timeout
    
    def _create_packet(self, code, attributes):
        """Create RADIUS packet"""
        identifier = secrets.randbelow(256)
        authenticator = secrets.token_bytes(16)
        
        # Encode attributes
        attr_data = b''
        for attr_type, attr_value in attributes:
            if isinstance(attr_value, str):
                attr_value = attr_value.encode()
            attr_data += struct.pack('BB', attr_type, len(attr_value) + 2) + attr_value
        
        # Create packet without Message-Authenticator
        length = 20 + len(attr_data)
        packet = struct.pack('!BBH16s', code, identifier, length, authenticator) + attr_data
        
        # Calculate Message-Authenticator (HMAC-MD5)
        message_auth = hashlib.md5(packet + self.nas_secret).digest()
        
        # Recreate packet with correct authenticator
        packet = struct.pack('!BBH16s', code, identifier, length, message_auth) + attr_data
        
        return packet, identifier
    
    def disconnect_user(self, username=None, session_id=None, framed_ip=None):
        """
        Send Disconnect-Request to NAS
        
        Args:
            username: Username to disconnect
            session_id: Acct-Session-Id to disconnect
            framed_ip: Framed-IP-Address to disconnect
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        if not any([username, session_id, framed_ip]):
            return {'success': False, 'message': 'Must provide username, session_id, or framed_ip'}
        
        # Build attributes
        attributes = []
        if username:
            attributes.append((1, username))  # User-Name
        if session_id:
            attributes.append((44, session_id))  # Acct-Session-Id
        if framed_ip:
            # Convert IP to bytes
            ip_bytes = socket.inet_aton(framed_ip)
            attributes.append((8, ip_bytes))  # Framed-IP-Address
        
        try:
            # Create packet
            packet, identifier = self._create_packet(self.DISCONNECT_REQUEST, attributes)
            
            # Send to NAS
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            sock.sendto(packet, (self.nas_ip, self.coa_port))
            
            # Wait for response
            response, _ = sock.recvfrom(4096)
            sock.close()
            
            # Parse response
            code = struct.unpack('!B', response[0:1])[0]
            
            if code == self.DISCONNECT_ACK:
                return {'success': True, 'message': 'User disconnected successfully'}
            elif code == self.DISCONNECT_NAK:
                return {'success': False, 'message': 'Disconnect rejected by NAS'}
            else:
                return {'success': False, 'message': f'Unexpected response code: {code}'}
        
        except socket.timeout:
            return {'success': False, 'message': 'Timeout waiting for NAS response'}
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
