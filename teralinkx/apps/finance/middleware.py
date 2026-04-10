# apps/finance/middleware.py
"""
Finance App Middleware
Centralized error handling and logging.
"""
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.exceptions import APIException
import logging
import traceback

logger = logging.getLogger(__name__)


class FinanceErrorHandlerMiddleware:
    """Centralized error handling for finance app"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        """Handle exceptions and return consistent error responses"""
        
        # Log the exception
        logger.error(
            f"Exception in {request.path}: {str(exception)}",
            exc_info=True,
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user': str(request.user) if request.user.is_authenticated else 'anonymous'
            }
        )
        
        # Determine error details
        if isinstance(exception, APIException):
            status_code = exception.status_code
            error_code = exception.default_code.upper()
            message = str(exception.detail)
        elif isinstance(exception, ValueError):
            status_code = 400
            error_code = 'INVALID_INPUT'
            message = str(exception)
        elif isinstance(exception, PermissionError):
            status_code = 403
            error_code = 'PERMISSION_DENIED'
            message = 'You do not have permission to perform this action'
        else:
            status_code = 500
            error_code = 'INTERNAL_SERVER_ERROR'
            message = 'An unexpected error occurred'
        
        # Build error response
        error_response = {
            'error': {
                'code': error_code,
                'message': message,
                'timestamp': timezone.now().isoformat(),
                'path': request.path
            }
        }
        
        # Add stack trace in debug mode
        from django.conf import settings
        if settings.DEBUG:
            error_response['error']['traceback'] = traceback.format_exc()
        
        return JsonResponse(error_response, status=status_code)


class RequestLoggingMiddleware:
    """Log all API requests for monitoring"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log request
        if request.path.startswith('/api/') or request.path.startswith('/finance/'):
            logger.info(
                f"{request.method} {request.path}",
                extra={
                    'request_method': request.method,
                    'request_path': request.path,
                    'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                    'ip_address': self.get_client_ip(request)
                }
            )
        
        # Process request
        response = self.get_response(request)
        
        # Log response
        if request.path.startswith('/api/') or request.path.startswith('/finance/'):
            logger.info(
                f"{request.method} {request.path} - {response.status_code}",
                extra={
                    'request_method': request.method,
                    'request_path': request.path,
                    'response_status': response.status_code,
                    'user': str(request.user) if request.user.is_authenticated else 'anonymous'
                }
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SensitiveDataFilterMiddleware:
    """Filter sensitive data from logs"""
    
    SENSITIVE_FIELDS = [
        'password', 'token', 'secret', 'api_key', 'access_token',
        'refresh_token', 'card_number', 'cvv', 'pin'
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Filter sensitive data from request body
        if hasattr(request, 'data'):
            self.filter_sensitive_data(request.data)
        
        response = self.get_response(request)
        return response
    
    def filter_sensitive_data(self, data):
        """Recursively filter sensitive fields from data"""
        if isinstance(data, dict):
            for key in list(data.keys()):
                if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                    data[key] = '***FILTERED***'
                elif isinstance(data[key], (dict, list)):
                    self.filter_sensitive_data(data[key])
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self.filter_sensitive_data(item)
