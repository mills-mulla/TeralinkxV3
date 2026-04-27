# views/package_views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q, Count, Sum, Avg
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

            avg_price = PackageType.objects.aggregate(avg=Sum('price'))['avg'] or 0
            if total_packages > 0:
                avg_price = avg_price / total_packages

            by_category = PackageType.objects.values('category').annotate(count=Count('id'))
            by_tier = PackageType.objects.values('tier').annotate(count=Count('id'))

            # Per-package sales breakdown — grouped by package id/name/code
            package_sales = PackageType.objects.annotate(
                total_dispatched=Count('dispatchvoucher'),
                currently_active=Count('dispatchvoucher', filter=Q(dispatchvoucher__status='active')),
                expired_count=Count('dispatchvoucher', filter=Q(dispatchvoucher__status='expired')),
                cancelled_count=Count('dispatchvoucher', filter=Q(dispatchvoucher__status='cancelled')),
                revenue=Sum('dispatchvoucher__price_paid')
            ).values(
                'id', 'name', 'code', 'price', 'tier', 'category',
                'total_dispatched', 'currently_active', 'expired_count',
                'cancelled_count', 'revenue', 'sold_quantity'
            ).order_by('-total_dispatched')

            return Response({
                'total_packages': total_packages,
                'active_packages': active_packages,
                'public_packages': public_packages,
                'average_price': float(avg_price),
                'by_category': list(by_category),
                'by_tier': list(by_tier),
                'package_sales': [
                    {**p, 'revenue': float(p['revenue'] or 0)}
                    for p in package_sales
                ]
            })
        except Exception as e:
            logger.error(f"Error fetching package stats: {e}")
            return Response({'error': str(e)}, status=500)

    @action(detail=True, methods=['post'])
    def sync_sales(self, request, pk=None):
        """Recalculate sold_quantity from all dispatched vouchers (Option B - includes cancelled)"""
        pkg = self.get_object()
        actual = DispatchVoucher.objects.filter(package=pkg).count()
        pkg.sold_quantity = actual
        pkg.save(update_fields=['sold_quantity'])
        return Response({'sold_quantity': actual})

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        pkg = self.get_object()
        pkg.pk = None
        pkg.name = f"{pkg.name} (Copy)"
        pkg.code = f"{pkg.code}-COPY"
        pkg.is_active = False
        pkg.sold_quantity = 0
        pkg.save()
        return Response(PackageTypeSerializer(pkg).data)

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        field_map = {
            'activate': {'is_active': True},
            'deactivate': {'is_active': False},
            'feature': {'is_featured': True},
            'unfeature': {'is_featured': False}
        }
        if action not in field_map:
            return Response({'error': 'Invalid action'}, status=400)
        PackageType.objects.filter(id__in=ids).update(**field_map[action])
        return Response({'updated': len(ids)})

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Package analytics with period comparisons"""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        pkg_id = request.query_params.get('package_id')  # optional filter

        def period_stats(start, end, pkg_id=None):
            qs = DispatchVoucher.objects.filter(activated_at__gte=start, activated_at__lt=end)
            if pkg_id:
                qs = qs.filter(package_id=pkg_id)
            return qs.values('package__id', 'package__name', 'package__code', 'package__tier').annotate(
                sold=Count('id'),
                revenue=Sum('price_paid'),
                avg_price=Avg('price_paid'),
                active=Count('id', filter=Q(status='active')),
                expired=Count('id', filter=Q(status='expired')),
                cancelled=Count('id', filter=Q(status='cancelled')),
            ).order_by('-sold')

        def fmt(qs):
            return [{
                'package_id': r['package__id'],
                'name': r['package__name'],
                'code': r['package__code'],
                'tier': r['package__tier'],
                'sold': r['sold'],
                'revenue': float(r['revenue'] or 0),
                'avg_price': float(r['avg_price'] or 0),
                'active': r['active'],
                'expired': r['expired'],
                'cancelled': r['cancelled'],
            } for r in qs]

        # Define all periods
        periods = {
            'this_week':   (now - timedelta(days=7),   now),
            'last_week':   (now - timedelta(days=14),  now - timedelta(days=7)),
            'this_month':  (now - timedelta(days=30),  now),
            'last_month':  (now - timedelta(days=60),  now - timedelta(days=30)),
            'this_quarter':(now - timedelta(days=90),  now),
            'last_quarter':(now - timedelta(days=180), now - timedelta(days=90)),
            'this_year':   (now - timedelta(days=365), now),
        }

        result = {k: fmt(period_stats(v[0], v[1], pkg_id)) for k, v in periods.items()}

        # Daily trend for last 30 days (for chart)
        from django.db.models.functions import TruncDate
        trend_qs = DispatchVoucher.objects.filter(activated_at__gte=now - timedelta(days=30))
        if pkg_id:
            trend_qs = trend_qs.filter(package_id=pkg_id)
        trend = trend_qs.annotate(date=TruncDate('activated_at')).values('date', 'package__name', 'package__code').annotate(
            sold=Count('id'), revenue=Sum('price_paid')
        ).order_by('date')
        result['daily_trend'] = [{
            'date': str(r['date']),
            'name': r['package__name'],
            'code': r['package__code'],
            'sold': r['sold'],
            'revenue': float(r['revenue'] or 0)
        } for r in trend]

        # All-time totals per package
        all_time = DispatchVoucher.objects.all()
        if pkg_id:
            all_time = all_time.filter(package_id=pkg_id)
        all_time = all_time.values('package__id','package__name','package__code','package__tier','package__price').annotate(
            total_sold=Count('id'), total_revenue=Sum('price_paid'), currently_active=Count('id', filter=Q(status='active'))
        ).order_by('-total_sold')
        result['all_time'] = [{
            'package_id': r['package__id'], 'name': r['package__name'],
            'code': r['package__code'], 'tier': r['package__tier'],
            'price': float(r['package__price'] or 0),
            'total_sold': r['total_sold'],
            'total_revenue': float(r['total_revenue'] or 0),
            'currently_active': r['currently_active']
        } for r in all_time]

        return Response(result)


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

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        v = self.get_object()
        v.status = 'suspended'
        v.save()
        return Response({'status': 'suspended'})

    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        v = self.get_object()
        v.status = 'active'
        v.save()
        return Response({'status': 'active'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        v = self.get_object()
        v.status = 'cancelled'
        v.save()
        return Response({'status': 'cancelled'})

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        status_map = {'suspend': 'suspended', 'reactivate': 'active', 'cancel': 'cancelled'}
        if action not in status_map:
            return Response({'error': 'Invalid action'}, status=400)
        DispatchVoucher.objects.filter(id__in=ids).update(status=status_map[action])
        return Response({'updated': len(ids)})

    @action(detail=False, methods=['get'])
    def form_options(self, request):
        from locations.models import Location
        from packages.models import PackageType
        from users.models import ClientH
        return Response({
            'clients': list(ClientH.objects.values('id', 'account', 'user__username').order_by('account')[:200]),
            'packages': list(PackageType.objects.filter(is_active=True).values('id', 'name', 'price').order_by('name')),
            'locations': list(Location.objects.filter(is_active=True).values('id', 'name', 'code').order_by('name'))
        })


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

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Bulk activate/deactivate/delete coupons"""
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        if not ids or action not in ['activate', 'deactivate', 'delete']:
            return Response({'error': 'Invalid action or ids'}, status=400)
        qs = Coupon.objects.filter(id__in=ids)
        if action == 'activate':
            qs.update(is_active=True)
        elif action == 'deactivate':
            qs.update(is_active=False)
        elif action == 'delete':
            qs.delete()
        return Response({'success': True, 'affected': len(ids)})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        coupon = self.get_object()
        coupon.is_active = True
        coupon.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': True})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        coupon = self.get_object()
        coupon.is_active = False
        coupon.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': False})

    @action(detail=False, methods=['get'])
    def form_options(self, request):
        """Return dropdown options for coupon form"""
        packages = PackageType.objects.filter(is_active=True).values('id', 'name', 'category', 'tier')
        return Response({
            'packages': list(packages),
            'coupon_types': [{'value': k, 'label': v} for k, v in Coupon.COUPON_TYPES],
            'applicable_to': [{'value': k, 'label': v} for k, v in Coupon.APPLICABLE_TO],
            'categories': [{'value': k, 'label': v} for k, v in PackageType.PACKAGE_CATEGORIES],
            'tiers': [{'value': k, 'label': v} for k, v in PackageType.TIERS],
        })


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

    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """Bulk activate/deactivate/delete promotions"""
        action = request.data.get('action')
        ids = request.data.get('ids', [])
        if not ids or action not in ['activate', 'deactivate', 'delete']:
            return Response({'error': 'Invalid action or ids'}, status=400)
        qs = FeaturedPromotion.objects.filter(id__in=ids)
        if action == 'activate':
            qs.update(is_active=True)
        elif action == 'deactivate':
            qs.update(is_active=False)
        elif action == 'delete':
            qs.delete()
        return Response({'success': True, 'affected': len(ids)})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        promo = self.get_object()
        promo.is_active = True
        promo.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': True})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        promo = self.get_object()
        promo.is_active = False
        promo.save(update_fields=['is_active'])
        return Response({'success': True, 'is_active': False})

    @action(detail=False, methods=['get'])
    def form_options(self, request):
        """Return dropdown options for promotion form"""
        packages = PackageType.objects.filter(is_active=True).values('id', 'name', 'price')
        coupons = Coupon.objects.filter(is_active=True).values('id', 'code', 'name', 'coupon_type', 'discount_value')
        return Response({
            'packages': list(packages),
            'coupons': list(coupons),
            'promotion_types': [{'value': k, 'label': v} for k, v in FeaturedPromotion.PROMOTION_TYPES],
        })


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
