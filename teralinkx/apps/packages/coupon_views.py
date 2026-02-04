from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from decimal import Decimal

from packages.models import Coupon, PackageType
from users.models import ClientH


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_coupon(request):
    """Validate coupon and calculate discount"""
    try:
        client = get_object_or_404(ClientH, user=request.user)
        coupon_code = request.data.get('coupon_code')
        package_id = request.data.get('package_id')
        
        if not coupon_code or not package_id:
            return Response({'error': 'coupon_code and package_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get coupon
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if coupon is expired
        if coupon.valid_until < timezone.now():
            return Response({'error': 'Coupon has expired'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check usage limit
        if coupon.total_uses >= coupon.max_uses:
            return Response({'error': 'Coupon usage limit reached'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get package
        try:
            package = PackageType.objects.get(id=package_id)
        except PackageType.DoesNotExist:
            return Response({'error': 'Package not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate discount
        package_price = Decimal(str(package.price))
        
        if coupon.coupon_type == 'percentage':
            discount_amount = package_price * (coupon.discount_value / 100)
        else:  # fixed amount
            discount_amount = min(coupon.discount_value, package_price)
        
        # Apply minimum order value check
        if coupon.minimum_order_value and package_price < coupon.minimum_order_value:
            return Response({
                'error': f'Minimum order value of KES {coupon.minimum_order_value} required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        final_price = max(Decimal('0'), package_price - discount_amount)
        
        return Response({
            'valid': True,
            'coupon': {
                'code': coupon.code,
                'name': coupon.name,
                'discount_value': float(coupon.discount_value),
                'coupon_type': coupon.coupon_type,
                'discount_amount': float(discount_amount)
            },
            'pricing': {
                'original_price': float(package_price),
                'discount_amount': float(discount_amount),
                'final_price': float(final_price),
                'savings': float(discount_amount)
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_coupon(request):
    """Apply coupon and mark as used"""
    try:
        client = get_object_or_404(ClientH, user=request.user)
        coupon_code = request.data.get('coupon_code')
        
        if not coupon_code:
            return Response({'error': 'coupon_code required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get and validate coupon
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already at usage limit
        if coupon.total_uses >= coupon.max_uses:
            return Response({'error': 'Coupon usage limit reached'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Increment usage count
        coupon.total_uses += 1
        
        # If max uses reached, deactivate coupon
        if coupon.total_uses >= coupon.max_uses:
            coupon.is_active = False
        
        coupon.save()
        
        return Response({
            'success': True,
            'message': 'Coupon applied successfully',
            'remaining_uses': coupon.max_uses - coupon.total_uses
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)