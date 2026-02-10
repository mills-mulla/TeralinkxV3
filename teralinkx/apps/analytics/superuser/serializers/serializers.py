# serializers/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import ClientH
from packages.models import DispatchVoucher
from finance.models import PaymentTransaction, TransactionQueue

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientH
        fields = '__all__'
    
    def get_profile_image(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'