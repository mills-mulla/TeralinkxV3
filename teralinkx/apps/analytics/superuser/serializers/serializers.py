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
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = ClientH
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'