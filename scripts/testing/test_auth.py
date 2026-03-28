#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append('/home/teralinkx/TeralinkxV3/teralinkx')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teralinkx.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from packages.rewards_views import get_user_coupons
from users.models import ClientH

# Create test user and client
try:
    user = User.objects.get(username='+254714787999')
    print(f"Found user: {user.username}")
except User.DoesNotExist:
    print("User +254714787999 not found")
    sys.exit(1)

try:
    client = ClientH.objects.get(user=user)
    print(f"Found client: {client.id}")
except ClientH.DoesNotExist:
    print("Client not found for user")
    sys.exit(1)

# Create JWT token
token = AccessToken.for_user(user)
print(f"Generated token: {str(token)[:50]}...")

# Create request with token
factory = RequestFactory()
request = factory.get('/api/rewards/coupons/')
request.user = user

# Add authorization header
request.META['HTTP_AUTHORIZATION'] = f'Bearer {str(token)}'

# Test the view
try:
    response = get_user_coupons(request)
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()