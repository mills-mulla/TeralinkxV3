# apps/packages/views/available_voucher.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser  # Admin only for all operations

class AvailableVoucherAPIView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can access available vouchers
    
    def post(self, request):
        """Create available vouchers - ADMIN ONLY"""
        # ... keep your existing post method code
    
    def get(self, request):
        """Get available vouchers - ADMIN ONLY"""
        # ... keep your existing get method code