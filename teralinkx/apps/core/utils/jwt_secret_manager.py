# core/utils/jwt_secret_manager.py
import os
import secrets
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

class JWTSecretManager:
    """
    Manages JWT secrets with persistence across container restarts.
    Ensures tokens remain valid even when backend restarts.
    """
    
    # Use persistent volume mount for Docker
    SECRET_DIR = '/app/data/secrets'
    SECRET_FILE = os.path.join(SECRET_DIR, 'jwt_secret.key')
    BACKUP_SECRET_FILE = os.path.join(SECRET_DIR, 'jwt_secret_backup.key')
    
    @classmethod
    def get_or_create_jwt_secret(cls) -> str:
        """
        Get existing JWT secret or create a new one.
        Stores secret in persistent volume to survive container restarts.
        """
        try:
            # Try to read existing secret
            if os.path.exists(cls.SECRET_FILE):
                with open(cls.SECRET_FILE, 'r') as f:
                    secret = f.read().strip()
                    if secret and len(secret) >= 32:  # Minimum security requirement
                        logger.info("✅ JWT secret loaded from persistent storage")
                        return secret
                    else:
                        logger.warning("⚠️ Invalid JWT secret found, generating new one")
            
            # Try backup secret
            if os.path.exists(cls.BACKUP_SECRET_FILE):
                with open(cls.BACKUP_SECRET_FILE, 'r') as f:
                    secret = f.read().strip()
                    if secret and len(secret) >= 32:
                        logger.info("✅ JWT secret restored from backup")
                        # Restore to primary location
                        cls._save_secret(secret)
                        return secret
            
            # Generate new secret if none exists
            logger.info("🔑 Generating new JWT secret...")
            secret = cls._generate_new_secret()
            cls._save_secret(secret)
            
            return secret
            
        except Exception as e:
            logger.error(f"❌ Failed to manage JWT secret: {e}")
            # Fallback to Django's SECRET_KEY if all else fails
            logger.warning("⚠️ Using Django SECRET_KEY as JWT secret fallback")
            return settings.SECRET_KEY
    
    @classmethod
    def _generate_new_secret(cls) -> str:
        """Generate a cryptographically secure secret."""
        return secrets.token_urlsafe(64)
    
    @classmethod
    def _save_secret(cls, secret: str) -> bool:
        """Save secret to persistent storage with backup."""
        try:
            # Ensure directory exists
            os.makedirs(cls.SECRET_DIR, exist_ok=True)
            
            # Save primary secret
            with open(cls.SECRET_FILE, 'w') as f:
                f.write(secret)
            
            # Save backup secret
            with open(cls.BACKUP_SECRET_FILE, 'w') as f:
                f.write(secret)
            
            # Set secure permissions (readable only by owner)
            os.chmod(cls.SECRET_FILE, 0o600)
            os.chmod(cls.BACKUP_SECRET_FILE, 0o600)
            
            logger.info("✅ JWT secret saved to persistent storage with backup")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save JWT secret: {e}")
            return False
    
    @classmethod
    def rotate_secret(cls) -> tuple[str, str]:
        """
        Rotate JWT secret while keeping old one for token validation.
        Returns (new_secret, old_secret)
        """
        try:
            # Get current secret
            old_secret = cls.get_or_create_jwt_secret()
            
            # Generate new secret
            new_secret = cls._generate_new_secret()
            
            # Save old secret as backup
            old_backup_file = os.path.join(cls.SECRET_DIR, 'jwt_secret_old.key')
            with open(old_backup_file, 'w') as f:
                f.write(old_secret)
            os.chmod(old_backup_file, 0o600)
            
            # Save new secret
            cls._save_secret(new_secret)
            
            logger.info("🔄 JWT secret rotated successfully")
            return new_secret, old_secret
            
        except Exception as e:
            logger.error(f"❌ JWT secret rotation failed: {e}")
            raise
    
    @classmethod
    def get_validation_secrets(cls) -> list[str]:
        """
        Get all secrets that should be used for token validation.
        Includes current secret and recent old secrets for graceful rotation.
        """
        secrets_list = []
        
        try:
            # Current secret
            current_secret = cls.get_or_create_jwt_secret()
            secrets_list.append(current_secret)
            
            # Old secret (for graceful rotation)
            old_secret_file = os.path.join(cls.SECRET_DIR, 'jwt_secret_old.key')
            if os.path.exists(old_secret_file):
                with open(old_secret_file, 'r') as f:
                    old_secret = f.read().strip()
                    if old_secret and old_secret != current_secret:
                        secrets_list.append(old_secret)
            
            return secrets_list
            
        except Exception as e:
            logger.error(f"❌ Failed to get validation secrets: {e}")
            return [settings.SECRET_KEY]  # Fallback
    
    @classmethod
    def cleanup_old_secrets(cls, keep_days: int = 7) -> None:
        """Clean up old secret files after specified days."""
        try:
            import time
            
            old_secret_file = os.path.join(cls.SECRET_DIR, 'jwt_secret_old.key')
            if os.path.exists(old_secret_file):
                file_age = time.time() - os.path.getmtime(old_secret_file)
                if file_age > (keep_days * 24 * 3600):  # Convert days to seconds
                    os.remove(old_secret_file)
                    logger.info(f"🧹 Cleaned up old JWT secret (age: {file_age/86400:.1f} days)")
                    
        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup old secrets: {e}")

# Initialize JWT secret on module import
JWT_SECRET = JWTSecretManager.get_or_create_jwt_secret()