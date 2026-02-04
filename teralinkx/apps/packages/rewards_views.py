# apps/packages/rewards_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import models

from core.services.rewards_service import RewardsService
from users.models import ClientH


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reward_summary(request):
    """Get user's complete reward summary"""
    try:
        client = get_object_or_404(ClientH, user=request.user)
        summary = RewardsService.get_user_reward_summary(client)
        return Response(summary)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_rewards(request):
    """Get rewards available for redemption"""
    try:
        client = get_object_or_404(ClientH, user=request.user)
        rewards = RewardsService.get_available_rewards(client)
        return Response({'rewards': rewards})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def redeem_reward(request):
    """Redeem points for a discount coupon"""
    try:
        client = get_object_or_404(ClientH, user=request.user)
        points_cost = request.data.get('points_cost')
        discount_percentage = request.data.get('discount_percentage')
        
        if not points_cost or not discount_percentage:
            return Response(
                {'error': 'points_cost and discount_percentage are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, message, coupon = RewardsService.redeem_discount_coupon(
            client, points_cost, discount_percentage
        )
        
        if success:
            return Response({
                'success': True,
                'message': message,
                'coupon_code': coupon.code,
                'remaining_points': client.reward_points
            })
        else:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_coupons(request):
    """Get user's available coupon codes"""
    try:
        client = get_object_or_404(ClientH, user=request.user)
        
        # Get user's reward coupons from their point transactions
        from packages.models import Coupon, PointTransaction
        from django.utils import timezone
        
        # Get coupon codes from user's redemption transactions
        redemption_transactions = PointTransaction.objects.filter(
            user=client,
            transaction_type='redeemed_coupon',
            related_coupon__isnull=False
        ).select_related('related_coupon')
        
        coupon_data = []
        for transaction in redemption_transactions:
            coupon = transaction.related_coupon
            # Only include if coupon is still valid and not used
            if (coupon.is_active and 
                coupon.valid_until > timezone.now() and
                coupon.total_uses < coupon.max_uses):
                
                coupon_data.append({
                    'code': coupon.code,
                    'name': coupon.name,
                    'discount_value': float(coupon.discount_value),
                    'coupon_type': coupon.coupon_type,
                    'valid_until': coupon.valid_until.isoformat(),
                    'points_cost': coupon.points_cost,
                    'description': coupon.description
                })
        return Response({'coupons': coupon_data})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_point_history(request):
    """Get user's point transaction history"""
    try:
        client = get_object_or_404(ClientH, user=request.user)
        transactions = client.point_transactions.order_by('-created_at')[:50]
        
        history = [
            {
                'id': t.id,
                'type': t.transaction_type,
                'points': t.points,
                'description': t.description,
                'date': t.created_at.isoformat(),
                'coupon_code': t.related_coupon.code if t.related_coupon else None,
                'voucher_code': t.related_voucher.voucher_code if t.related_voucher else None
            }
            for t in transactions
        ]
        
        return Response({'transactions': history})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)