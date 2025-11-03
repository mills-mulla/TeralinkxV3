from django.middleware.csrf import get_token
from django.http import JsonResponse

def get_csrf_token(request):
    """Returns CSRF token for the current session"""
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})
