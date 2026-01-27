# apps/packages/package.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from django.utils import timezone

from .models import PackageType, FeaturedPromotion
from core.serializers.package_serializer import PackageTypeSerializer


class PackageAPIView(APIView):
    """Get internet packages - JWT authenticated users"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get available internet packages for authenticated user
        JWT token determines user permissions and location
        """
        # Get user from JWT token
        user = request.user
        
        # Get query parameters
        category = request.query_params.get('category')
        tier = request.query_params.get('tier')
        location_id = request.query_params.get('location_id')
        featured_only = request.query_params.get('featured')
        
        # Base query - only active, public packages
        packages = PackageType.objects.filter(is_active=True, is_public=True)
        
        # Apply filters
        if category:
            packages = packages.filter(category=category)
        if tier:
            packages = packages.filter(tier=tier)
        if location_id:
            # Filter packages available at specific location
            packages = packages.filter(
                Q(locations__id=location_id) | Q(locations__isnull=True)
            ).distinct()
        if featured_only and featured_only.lower() == 'true':
            packages = packages.filter(is_featured=True)
        
        # Order packages (featured first, then by display order)
        packages = packages.order_by('-is_featured', 'display_order', 'tier', 'price')
        
        serializer = PackageTypeSerializer(packages, many=True)
        
        # Get user's location if available (from client profile)
        user_location_id = None
        try:
            if hasattr(user, 'client_profile') and user.client_profile.current_location:
                user_location_id = user.client_profile.current_location.id
        except:
            pass
        
        return Response({
            'user': user.username,
            'user_location_id': user_location_id,
            'count': packages.count(),
            'packages': serializer.data
        })


class PackageCreateAPIView(APIView):
    """Create new internet package - ADMIN ONLY (JWT admin)"""
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        """
        Create new internet package
        JWT token must be from admin user
        """
        serializer = PackageTypeSerializer(data=request.data)
        if serializer.is_valid():
            package = serializer.save()
            return Response({
                'message': 'Package created successfully',
                'created_by_admin': request.user.username,  # JWT admin
                'package': PackageTypeSerializer(package).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': 'Invalid package data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PackageDetailAPIView(APIView):
    """Get detailed information about a specific package"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, package_id):
        """
        Get package details including any active promotions
        """
        try:
            package = PackageType.objects.get(
                id=package_id, 
                is_active=True,
                is_public=True
            )
        except PackageType.DoesNotExist:
            return Response({
                'error': 'Package not found or not available'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PackageTypeSerializer(package)
        
        # Get active promotions for this package
        now = timezone.now()
        active_promotions = FeaturedPromotion.objects.filter(
            package=package,
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
        
        response_data = serializer.data
        response_data['active_promotions'] = []
        
        for promotion in active_promotions:
            promotion_data = {
                'promotion_id': promotion.id,
                'name': promotion.name,
                'headline': promotion.headline,
                'description': promotion.description,
                'promotion_type': promotion.promotion_type,
                'end_date': promotion.end_date,
                'has_coupon': bool(promotion.coupon),
            }
            
            if promotion.coupon and promotion.coupon.is_valid:
                promotion_data['coupon'] = {
                    'code': promotion.coupon.code,
                    'discount_message': promotion.discount_message,
                    'final_price': float(promotion.final_price),
                }
            
            response_data['active_promotions'].append(promotion_data)
        
        return Response(response_data)


class FeaturedPackagesAPIView(APIView):
    """Get featured packages with promotions"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get featured packages and their active promotions
        """
        # Get user's location if available
        user = request.user
        location_id = request.query_params.get('location_id')
        
        if not location_id and hasattr(user, 'client_profile'):
            try:
                if user.client_profile.current_location:
                    location_id = user.client_profile.current_location.id
            except:
                pass
        
        # Get featured packages
        featured_packages = PackageType.objects.filter(
            is_featured=True,
            is_active=True,
            is_public=True
        ).order_by('display_order', 'tier', 'price')
        
        # Apply location filter if provided
        if location_id:
            featured_packages = featured_packages.filter(
                Q(locations__id=location_id) | Q(locations__isnull=True)
            ).distinct()
        
        packages_data = []
        for package in featured_packages:
            package_data = PackageTypeSerializer(package).data
            
            # Get active promotions for this package
            active_promotions = FeaturedPromotion.objects.filter(
                package=package,
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )
            
            if location_id and active_promotions.exists():
                active_promotions = active_promotions.filter(
                    Q(locations__id=location_id) | Q(locations__isnull=True)
                )
            
            package_data['active_promotions'] = []
            for promo in active_promotions:
                promo_data = {
                    'id': promo.id,
                    'name': promo.name,
                    'headline': promo.headline,
                    'has_coupon': bool(promo.coupon),
                }
                if promo.coupon and promo.coupon.is_valid:
                    promo_data['coupon'] = {
                        'code': promo.coupon.code,
                        'discount_message': promo.discount_message,
                    }
                package_data['active_promotions'].append(promo_data)
            
            packages_data.append(package_data)
        
        return Response({
            'location_id': location_id,
            'count': len(packages_data),
            'featured_packages': packages_data
        })