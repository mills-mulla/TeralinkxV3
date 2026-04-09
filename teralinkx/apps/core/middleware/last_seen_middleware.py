# core/middleware/last_seen_middleware.py
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class LastSeenMiddleware(MiddlewareMixin):
    """
    Middleware to update user's last_seen timestamp on every authenticated request.
    This enables real-time availability tracking for notifications and user status.
    """
    
    def process_request(self, request):
        """Update last_seen for authenticated users on every request"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            try:
                # Check if user has client profile
                if hasattr(request.user, 'client_profile'):
                    client = request.user.client_profile
                    
                    # Update last_seen timestamp
                    client.last_seen = timezone.now()
                    client.save(update_fields=['last_seen'])
                    
            except Exception as e:
                # Log error but don't break the request
                logger.warning(f"Failed to update last_seen for user {request.user.id}: {str(e)}")
        
        return None