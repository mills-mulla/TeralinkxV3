# teralinkx/jwt_manager.py - Persistent JWT Secret Management
import os
import secrets
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class JWTSecretManager:
    """
    Manages persistent JWT secrets to survive backend restarts.
    Stores secrets in persistent volume to maintain token validity.
    """
    
    def __init__(self):
        # Use local data path instead of Docker volume for development
        self.secret_dir = Path('./data/jwt')
        self.secret_file = self.secret_dir / 'jwt_secret.key'
        self.version_file = self.secret_dir / 'jwt_version.txt'
        
    def get_or_create_secret(self):
        """
        Get existing JWT secret or create new one if doesn't exist.
        Returns tuple: (secret, version, is_new)
        """
        try:
            # Ensure directory exists
            self.secret_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if secret exists
            if self.secret_file.exists():
                with open(self.secret_file, 'r') as f:
                    secret = f.read().strip()
                
                # Get version
                version = self._get_version()
                
                if secret and len(secret) >= 32:
                    logger.info(f"✅ Using existing JWT secret (version: {version})")
                    return secret, version, False
                else:
                    logger.warning("⚠️ Invalid existing secret, generating new one")
            
            # Generate new secret
            secret = self._generate_secret()
            version = self._increment_version()
            
            # Save secret
            with open(self.secret_file, 'w') as f:
                f.write(secret)
            
            # Set secure permissions
            os.chmod(self.secret_file, 0o600)
            
            logger.info(f"🔑 Generated new JWT secret (version: {version})")
            return secret, version, True
            
        except Exception as e:
            logger.error(f"💥 JWT secret management error: {e}")
            # Fallback to environment or generated secret
            fallback_secret = os.environ.get('DJANGO_SECRET_KEY', secrets.token_urlsafe(64))
            return fallback_secret, 'fallback', True
    
    def _generate_secret(self):
        """Generate cryptographically secure secret"""
        return secrets.token_urlsafe(64)
    
    def _get_version(self):
        """Get current secret version"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r') as f:
                    return f.read().strip()
            return 'v1'
        except:
            return 'v1'
    
    def _increment_version(self):
        """Increment and save version"""
        try:
            current_version = self._get_version()
            if current_version.startswith('v'):
                version_num = int(current_version[1:]) + 1
            else:
                version_num = 2
            
            new_version = f'v{version_num}'
            
            with open(self.version_file, 'w') as f:
                f.write(new_version)
            
            return new_version
        except:
            return 'v1'
    
    def rotate_secret(self):
        """
        Rotate JWT secret (for scheduled maintenance).
        Returns new secret and version.
        """
        try:
            # Backup old secret
            if self.secret_file.exists():
                backup_file = self.secret_dir / f'jwt_secret_backup_{self._get_version()}.key'
                os.rename(self.secret_file, backup_file)
            
            # Generate new secret
            secret = self._generate_secret()
            version = self._increment_version()
            
            # Save new secret
            with open(self.secret_file, 'w') as f:
                f.write(secret)
            
            os.chmod(self.secret_file, 0o600)
            
            logger.info(f"🔄 JWT secret rotated to version: {version}")
            return secret, version
            
        except Exception as e:
            logger.error(f"💥 JWT secret rotation error: {e}")
            raise

# Global instance
jwt_manager = JWTSecretManager()