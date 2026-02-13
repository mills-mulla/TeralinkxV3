from rest_framework import serializers
from .models import Advertisement, AdMedia

class AdMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdMedia
        fields = ['id', 'file', 'media_type', 'format', 'file_size', 'duration', 'created_at']

class AdvertisementSerializer(serializers.ModelSerializer):
    locations_list = serializers.SerializerMethodField()
    performance = serializers.SerializerMethodField()
    is_live_status = serializers.SerializerMethodField()
    media_files_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Advertisement
        fields = [
            'id', 'title', 'caption', 'ad_type', 'status', 'campaign_name',
            'image', 'video_file', 'video_thumbnail', 'audio_file',
            'brand_name', 'brand_logo', 'cta_text', 'cta_url', 'cta_color',
            'locations', 'locations_list', 'target_audience',
            'start_date', 'end_date', 'priority',
            'budget', 'bidding_strategy', 'cost_per_click', 'cost_per_impression',
            'impressions', 'clicks', 'total_spent',
            'is_active', 'performance', 'is_live_status', 'media_files_list',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['impressions', 'clicks', 'total_spent', 'created_at', 'updated_at']
    
    def get_locations_list(self, obj):
        return [{'id': loc.id, 'name': loc.name} for loc in obj.locations.all()]
    
    def get_performance(self, obj):
        return obj.get_performance_metrics()
    
    def get_is_live_status(self, obj):
        return obj.is_live
    
    def get_media_files_list(self, obj):
        return AdMediaSerializer(obj.media_files.all(), many=True).data
