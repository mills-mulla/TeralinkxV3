# Userprofile_serializer.py
from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import ClientH

class ClientProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = ClientH
        fields = ['first_name', 'image', 'account', 'balance', 'status']

    def update(self, instance, validated_data):
        # Update user's first_name
        user_data = validated_data.pop('user', {})
        if 'first_name' in user_data:
            instance.user.first_name = user_data['first_name']
            instance.user.save()

        # Update profile image if provided
        if 'image' in validated_data:
            instance.image = validated_data['image']

        return super().update(instance, validated_data)
