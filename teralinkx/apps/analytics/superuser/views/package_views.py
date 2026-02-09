# views/package_views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, Count, Sum
from django.utils import timezone
from packages.models import PackageType, DispatchVoucher, Coupon, FeaturedPromotion, PointTransaction
from ..serializers.package_serializers import (
    PackageTypeSerializer,
    DispatchVoucherSerializer,
    CouponSerializer,
    FeaturedPromotionSerializer,
    PointTransactionSerializer
)
import logging

logger = logging.getLogger(__name__)


class PackageTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for PackageType model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = PackageType.objects.all()
    serializer_class = PackageTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['id', 'name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by tier
        tier = self.request.query_params.get('tier', None)
        if tier:
            queryset = queryset.filter(tier=tier)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get package statistics"""
        try:
            total_packages = PackageType.objects.count()
            active_packages = PackageType.objects.filter(is_active=True).count()
            public_packages = PackageType.objects.filter(is_public=True).count()
            
            # Packages by category
            by_category = PackageType.objects.values('category').annotate(
                count=Count('id')
            )
            
            # Packages by tier
            by_tier = PackageType.objects.values('tier').annotate(
                count=Count('id')
            )
            
            return Response({
                'total_packages': total_packages,
                'active_packages': active_packages,
                'public_packages': public_packages,
                'by_category': list(by_category),
                'by_tier': list(by_tier)
            })
        except Exception as e:
            logger.error(f"Error fetching package stats: {e}")
            return Response({'error': str(e)}, status=500)


class DispatchVoucherViewSet(viewsets.ModelViewSet):
    """ViewSet for DispatchVoucher model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = DispatchVoucher.objects.all().select_related('user', 'package')
    serializer_class = DispatchVoucherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['voucher_code', 'user__username']
    ordering_fields = ['id', 'dispatch_expiry', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by client
        client_id = self.request.query_params.get('client_id', None)
        if client_id:
            queryset = queryset.filter(user_id=client_id)
        
        # Filter by expired
        expired = self.request.query_params.get('expired', None)
        if expired == 'true':
            queryset = queryset.filter(expires_at__lt=timezone.now())
        elif expired == 'false':
            queryset = queryset.filter(
                Q(expires_at__gte=timezone.now()) | Q(expires_at__isnull=True)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get voucher statistics"""
        try:
            total_vouchers = DispatchVoucher.objects.count()
            active_vouchers = DispatchVoucher.objects.filter(status='active').count()
            expired_vouchers = DispatchVoucher.objects.filter(
                expires_at__lt=timezone.now()
            ).count()
            
            # Total revenue
            total_revenue = DispatchVoucher.objects.aggregate(
                total=Sum('price_paid')
            )['total'] or 0
            
            return Response({
                'total_vouchers': total_vouchers,
                'active_vouchers': active_vouchers,
                'expired_vouchers': expired_vouchers,
                'total_revenue': float(total_revenue)
            })
        except Exception as e:
            logger.error(f"Error fetching voucher stats: {e}")
            return Response({'error': str(e)}, status=500)


class CouponViewSet(viewsets.ModelViewSet):
    """ViewSet for Coupon model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['id', 'created_at', 'valid_from', 'valid_until']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by reward status
        is_reward = self.request.query_params.get('is_reward', None)
        if is_reward is not None:
            queryset = queryset.filter(is_reward=is_reward.lower() == 'true')
        
        # Filter by valid coupons
        valid_only = self.request.query_params.get('valid_only', None)
        if valid_only == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                valid_from__lte=now,
                valid_until__gte=now
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get coupon statistics"""
        try:
            total_coupons = Coupon.objects.count()
            active_coupons = Coupon.objects.filter(is_active=True).count()
            reward_coupons = Coupon.objects.filter(is_reward=True).count()
            
            # Valid coupons
            now = timezone.now()
            valid_coupons = Coupon.objects.filter(
                is_active=True,
                valid_from__lte=now,
                valid_until__gte=now
            ).count()
            
            return Response({
                'total_coupons': total_coupons,
                'active_coupons': active_coupons,
                'reward_coupons': reward_coupons,
                'valid_coupons': valid_coupons
            })
        except Exception as e:
            logger.error(f"Error fetching coupon stats: {e}")
            return Response({'error': str(e)}, status=500)


class FeaturedPromotionViewSet(viewsets.ModelViewSet):
    """ViewSet for FeaturedPromotion model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = FeaturedPromotion.objects.all().select_related('package', 'coupon')
    serializer_class = FeaturedPromotionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'headline', 'description']
    ordering_fields = ['id', 'display_order', 'start_date', 'end_date']
    ordering = ['display_order', '-start_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by live promotions
        live_only = self.request.query_params.get('live_only', None)
        if live_only == 'true':
            queryset = [p for p in queryset if p.is_live]
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get promotion statistics"""
        try:
            total_promotions = FeaturedPromotion.objects.count()
            active_promotions = FeaturedPromotion.objects.filter(is_active=True).count()
            
            # Total performance
            totals = FeaturedPromotion.objects.aggregate(
                total_views=Sum('views'),
                total_clicks=Sum('clicks'),
                total_conversions=Sum('conversions')
            )
            
            return Response({
                'total_promotions': total_promotions,
                'active_promotions': active_promotions,
                'total_views': totals['total_views'] or 0,
                'total_clicks': totals['total_clicks'] or 0,
                'total_conversions': totals['total_conversions'] or 0
            })
        except Exception as e:
            logger.error(f"Error fetching promotion stats: {e}")
            return Response({'error': str(e)}, status=500)


class PointTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for PointTransaction model"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = PointTransaction.objects.all().select_related('user', 'related_voucher', 'related_coupon')
    serializer_class = PointTransactionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__account', 'description', 'transaction_type']
    ordering_fields = ['id', 'created_at', 'points']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('transaction_type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get point transaction statistics"""
        try:
            total_transactions = PointTransaction.objects.count()
            
            # Points by type
            earned = PointTransaction.objects.filter(points__gt=0).aggregate(
                total=Sum('points')
            )['total'] or 0
            
            redeemed = abs(PointTransaction.objects.filter(points__lt=0).aggregate(
                total=Sum('points')
            )['total'] or 0)
            
            # Transactions by type
            by_type = PointTransaction.objects.values('transaction_type').annotate(
                count=Count('id'),
                total_points=Sum('points')
            )
            
            return Response({
                'total_transactions': total_transactions,
                'total_earned': earned,
                'total_redeemed': redeemed,
                'net_points': earned - redeemed,
                'by_type': list(by_type)
            })
        except Exception as e:
            logger.error(f"Error fetching point transaction stats: {e}")
            return Response({'error': str(e)}, status=500)
