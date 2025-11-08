# apps/packages/views/dispatch_voucher.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import DispatchVoucher, PackageType
from core.serializers.package_serializer import DispatchVoucherSerializer

class DispatchVoucherAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Users can view their own vouchers
    
    def get(self, request):
        """Get user's own dispatch vouchers"""
        user_id = request.user.id  # Get from authenticated user
        
        vouchers = DispatchVoucher.objects.filter(user_id=user_id).order_by('-created_at')
        
        # Apply filters
        status_filter = request.query_params.get('status')
        is_active = request.query_params.get('is_active')
        
        if status_filter:
            vouchers = vouchers.filter(status=status_filter)
        if is_active is not None:
            if is_active.lower() == 'true':
                vouchers = vouchers.filter(
                    status='active',
                    expires_at__gte=timezone.now()
                )

        serializer = DispatchVoucherSerializer(vouchers, many=True)
        return Response({
            'count': vouchers.count(),
            'vouchers': serializer.data
        })

class DispatchVoucherCreateAPIView(APIView):
    permission_classes = [IsAdminUser]  # Only admins can create vouchers
    
    def post(self, request):
        """Create dispatch voucher - ADMIN ONLY"""
        try:
            package_id = request.data.get('package_id')
            user_id = request.data.get('user_id')
            location_id = request.data.get('location_id')
            price_paid = request.data.get('price_paid')
            allowed_mac_addresses = request.data.get('allowed_mac_addresses', [])
            is_roaming = request.data.get('is_roaming', False)

            if not all([package_id, user_id, location_id]):
                return Response({
                    'error': 'package_id, user_id, and location_id are required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create dispatch voucher
            voucher = DispatchVoucher.objects.create(
                package_id=package_id,
                user_id=user_id,
                location_id=location_id,
                price_paid=price_paid,
                allowed_mac_addresses=allowed_mac_addresses,
                is_roaming=is_roaming,
                home_location_id=location_id,
            )

            serializer = DispatchVoucherSerializer(voucher)
            return Response({
                'message': 'Voucher dispatched successfully',
                'voucher': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'error': f'Failed to create voucher: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)