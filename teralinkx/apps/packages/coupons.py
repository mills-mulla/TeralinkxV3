# apps/packages/coupons.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.packages.services import CouponService
from apps.packages.models import PackageType

class ValidateCouponAPI(APIView):
    """API to validate coupon code"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        package_id = request.data.get('package_id')
        
        if not code or not package_id:
            return Response(
                {'error': 'Coupon code and package ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            package = PackageType.objects.get(id=package_id, is_active=True)
        except PackageType.DoesNotExist:
            return Response(
                {'error': 'Package not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        is_valid, message = CouponService.validate_coupon(
            code, request.user, package
        )
        
        if is_valid:
            coupon = Coupon.objects.get(code=code)
            discount = coupon.calculate_discount(package.price)
            
            return Response({
                'valid': True,
                'message': message,
                'discount_amount': float(discount),
                'original_price': float(package.price),
                'final_price': float(package.price - discount),
                'coupon_type': coupon.coupon_type,
                'discount_value': float(coupon.discount_value),
            })
        
        return Response({
            'valid': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


class AvailableCouponsAPI(APIView):
    """API to get available coupons for a package"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        package_id = request.GET.get('package_id')
        
        if not package_id:
            return Response(
                {'error': 'Package ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            package = PackageType.objects.get(id=package_id, is_active=True)
        except PackageType.DoesNotExist:
            return Response(
                {'error': 'Package not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        coupons = CouponService.get_available_coupons_for_package(
            request.user, package
        )
        
        return Response({
            'package_id': package_id,
            'package_name': package.name,
            'available_coupons': coupons,
            'count': len(coupons)
        })