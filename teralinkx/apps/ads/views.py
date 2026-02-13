from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q
from .models import Advertisement
from .serializers import AdvertisementSerializer
from users.models import ClientH
from locations.models import Location
import logging
import re

logger = logging.getLogger(__name__)

class ActiveAdsView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access for ads
    
    def get(self, request):
        try:
            # Check cache first
            cache_key = 'active_ads_list'
            cached_ads = cache.get(cache_key)
            
            if cached_ads:
                return Response({
                    'success': True,
                    'ads': cached_ads,
                    'count': len(cached_ads),
                    'cached': True
                }, status=status.HTTP_200_OK)
            
            # Get user context if authenticated
            user = request.user if request.user.is_authenticated else None
            client = getattr(user, 'client_profile', None) if user else None
            location = getattr(client, 'current_location', None) if client else None
            
            # Get active ads with better filtering
            ads = Advertisement.objects.filter(
                Q(status='active') &
                Q(is_active=True) &
                Q(start_date__lte=timezone.now()) &
                Q(end_date__gte=timezone.now()) &
                Q(ad_type__in=['banner', 'video', 'audio', 'native', 'carousel'])
            ).select_related().prefetch_related('locations').order_by('-priority', '?')[:10]
            
            # Filter ads based on targeting
            filtered_ads = []
            for ad in ads:
                if ad.can_show_to_user(user=user, location=location):
                    ad_data = {
                        'id': ad.id,
                        'title': ad.title,
                        'caption': ad.caption,
                        'image': request.build_absolute_uri(ad.image.url) if ad.image else None,
                        'alt': ad.title,
                        'cta_text': ad.cta_text,
                        'cta_url': ad.cta_url,
                        'brand_name': ad.brand_name,
                        'brand_logo': request.build_absolute_uri(ad.brand_logo.url) if ad.brand_logo else None
                    }
                    
                    # Add type-specific media
                    if ad.ad_type == 'video' and ad.video_file:
                        ad_data['video_url'] = request.build_absolute_uri(ad.video_file.url)
                        ad_data['video_thumbnail'] = request.build_absolute_uri(ad.video_thumbnail.url) if ad.video_thumbnail else None
                    elif ad.ad_type == 'audio' and ad.audio_file:
                        ad_data['audio_url'] = request.build_absolute_uri(ad.audio_file.url)
                    elif ad.ad_type == 'carousel':
                        ad_data['carousel_images'] = ad.carousel_images
                    
                    filtered_ads.append(ad_data)
            
            # Cache for 5 minutes
            cache.set(cache_key, filtered_ads, 300)
            
            return Response({
                'success': True,
                'ads': filtered_ads,
                'count': len(filtered_ads)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching ads: {e}")
            return Response({
                'success': False,
                'ads': [],
                'error': 'Failed to fetch ads'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_duration_seconds(self, ad):
        """Convert duration to seconds"""
        if ad.ad_type == 'video' and ad.video_duration:
            return int(ad.video_duration.total_seconds())
        elif ad.ad_type == 'audio' and ad.audio_duration:
            return int(ad.audio_duration.total_seconds())
        else:
            return 15  # Default duration
    
    def _get_media_urls(self, ad, request):
        """Get media URLs for the ad"""
        media = {}
        
        if ad.ad_type == 'video':
            if ad.video_file:
                media['video'] = request.build_absolute_uri(ad.video_file.url)
            if ad.video_thumbnail:
                media['thumbnail'] = request.build_absolute_uri(ad.video_thumbnail.url)
        
        elif ad.ad_type == 'audio':
            if ad.audio_file:
                media['audio'] = request.build_absolute_uri(ad.audio_file.url)
        
        elif ad.ad_type in ['banner', 'native']:
            if ad.image:
                media['image'] = request.build_absolute_uri(ad.image.url)
        
        return media


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow unauthenticated tracking
def track_ad_interaction(request):
    """Track ad impressions and clicks"""
    try:
        data = request.data
        ad_id = data.get('ad_id')
        interaction_type = data.get('interaction_type')  # 'impression' or 'click'
        
        # Input validation and sanitization
        if not ad_id or not interaction_type:
            return Response({
                'success': False,
                'error': 'Missing ad_id or interaction_type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Sanitize ad_id - ensure it's a valid integer
        try:
            ad_id = int(re.sub(r'[^0-9]', '', str(ad_id)))
        except (ValueError, TypeError):
            return Response({
                'success': False,
                'error': 'Invalid ad_id format'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate interaction type
        if interaction_type not in ['impression', 'click']:
            return Response({
                'success': False,
                'error': 'Invalid interaction_type'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            ad = Advertisement.objects.get(id=ad_id)
        except Advertisement.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Ad not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if interaction_type == 'impression':
            ad.record_impression()
            logger.info(f"Recorded impression for ad {ad_id}")
        elif interaction_type == 'click':
            ad.record_click()
            logger.info(f"Recorded click for ad {ad_id}")
        
        # Clear cache when ad interactions are recorded
        cache.delete('active_ads_list')
        
        return Response({
            'success': True,
            'message': f'{interaction_type.title()} recorded successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error tracking ad interaction: {e}")
        return Response({
            'success': False,
            'error': 'Failed to track interaction'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AdvertisementManagementView(APIView):
    """Admin API for managing advertisements"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        """List all advertisements"""
        try:
            ads = Advertisement.objects.all().order_by('-created_at')
            serializer = AdvertisementSerializer(ads, many=True, context={'request': request})
            
            # Summary stats
            stats = {
                'total': ads.count(),
                'active': ads.filter(status='active').count(),
                'draft': ads.filter(status='draft').count(),
                'paused': ads.filter(status='paused').count(),
                'total_impressions': sum(ad.impressions for ad in ads),
                'total_clicks': sum(ad.clicks for ad in ads),
                'total_spent': float(sum(ad.total_spent for ad in ads))
            }
            
            return Response({
                'success': True,
                'ads': serializer.data,
                'stats': stats
            })
        except Exception as e:
            logger.error(f"Error fetching ads: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create new advertisement"""
        try:
            serializer = AdvertisementSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                ad = serializer.save()
                cache.delete('active_ads_list')
                return Response({
                    'success': True,
                    'message': 'Advertisement created successfully',
                    'ad': AdvertisementSerializer(ad, context={'request': request}).data
                }, status=status.HTTP_201_CREATED)
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating ad: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdvertisementDetailView(APIView):
    """Admin API for individual advertisement operations"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, pk):
        """Get single advertisement"""
        try:
            ad = Advertisement.objects.get(pk=pk)
            serializer = AdvertisementSerializer(ad, context={'request': request})
            return Response({'success': True, 'ad': serializer.data})
        except Advertisement.DoesNotExist:
            return Response({'error': 'Advertisement not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        """Update advertisement"""
        try:
            ad = Advertisement.objects.get(pk=pk)
            serializer = AdvertisementSerializer(ad, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                cache.delete('active_ads_list')
                return Response({
                    'success': True,
                    'message': 'Advertisement updated successfully',
                    'ad': serializer.data
                })
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Advertisement.DoesNotExist:
            return Response({'error': 'Advertisement not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        """Delete advertisement"""
        try:
            ad = Advertisement.objects.get(pk=pk)
            ad.delete()
            cache.delete('active_ads_list')
            return Response({
                'success': True,
                'message': 'Advertisement deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        except Advertisement.DoesNotExist:
            return Response({'error': 'Advertisement not found'}, status=status.HTTP_404_NOT_FOUND)
