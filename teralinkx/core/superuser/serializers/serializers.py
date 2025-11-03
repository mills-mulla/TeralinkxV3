# serializers/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import ClientH, DispatchVoucher, Transaction, RefundLog,DowntimeRecord

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ClientH
        fields = '__all__'

class EligibleClientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='clienth.user.username', read_only=True)
    email = serializers.CharField(source='clienth.user.email', read_only=True)
    current_balance = serializers.DecimalField(
        source='clienth.balance', 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    
    class Meta:
        model = DispatchVoucher
        fields = [
            'dispatch_id',
            'dispatch_account',
            'dispatch_price',
            'dispatch_package_duration',
            'dispatch_expiry',
            'total_download',
            'total_upload',
            'usage_limit',
            'username',
            'email',
            'current_balance'
        ]

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class RefundLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundLog
        fields = '__all__'



class DowntimeRecordSerializer(serializers.ModelSerializer):
    duration_hours = serializers.ReadOnlyField()
    formatted_duration = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    affected_users_percentage = serializers.ReadOnlyField()
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    
    class Meta:
        model = DowntimeRecord
        fields = [
            'id',
            'name',
            'start_time',
            'end_time',
            'duration_minutes',
            'duration_hours',
            'formatted_duration',
            'affected_services',
            'severity',
            'reason',
            'impact_level',
            'affected_regions',
            'estimated_affected_users',
            'affected_users_percentage',
            'resolution_notes',
            'resolved_by',
            'resolved_by_name',
            'resolution_time',
            'created_by',
            'created_by_name',
            'created_at',
            'updated_at',
            'is_resolved',
            'is_ongoing',
            'requires_follow_up',
            'follow_up_notes',
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'duration_minutes',
            'duration_hours',
            'formatted_duration',
            'is_ongoing',
            'affected_users_percentage',
        ]

    def validate(self, data):
        """
        Validate that end_time is after start_time
        """
        if data.get('start_time') and data.get('end_time'):
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time'
                })
        
        return data

    def create(self, validated_data):
        """
        Auto-set created_by user and calculate duration
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        
        # Calculate duration if not provided
        if 'duration_minutes' not in validated_data:
            if validated_data.get('start_time') and validated_data.get('end_time'):
                duration = validated_data['end_time'] - validated_data['start_time']
                validated_data['duration_minutes'] = int(duration.total_seconds() / 60)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Recalculate duration if times are updated
        """
        if 'start_time' in validated_data or 'end_time' in validated_data:
            start_time = validated_data.get('start_time', instance.start_time)
            end_time = validated_data.get('end_time', instance.end_time)
            
            if start_time and end_time:
                duration = end_time - start_time
                validated_data['duration_minutes'] = int(duration.total_seconds() / 60)
        
        return super().update(instance, validated_data)