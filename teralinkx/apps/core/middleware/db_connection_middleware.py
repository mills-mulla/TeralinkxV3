"""
Database connection management middleware
Ensures connections are properly closed after each request
"""
from django.db import connection, connections
from django.core.signals import request_finished
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionMiddleware:
    """Middleware to manage database connections and prevent leaks"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Close old connections after each request
        self.close_old_connections()
        
        return response
    
    def close_old_connections(self):
        """Close database connections that are too old"""
        for conn in connections.all():
            try:
                conn.close_if_unusable_or_obsolete()
            except Exception as e:
                logger.warning(f"Error closing database connection: {e}")
    
    def process_exception(self, request, exception):
        """Ensure connections are closed even on exceptions"""
        self.close_old_connections()
        return None
