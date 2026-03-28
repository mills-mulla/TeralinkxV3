# serializers/transaction_serializers.py
from rest_framework import serializers
from finance.models import PaymentTransaction, BalanceTransaction, TransactionQueue
from packages.models import PointTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    user_account = serializers.CharField(source='user.account', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'transaction_id', 'user', 'user_account', 'payment_method',
            'amount', 'currency', 'currency_code', 'exchange_rate', 'amount_base',
            'initiator', 'balance', 'date', 'result_code', 'result_desc',
            'merchant_request_id', 'checkout_request_id', 'transaction_time',
            'gateway_reference', 'status', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BalanceTransactionSerializer(serializers.ModelSerializer):
    user_account = serializers.CharField(source='user.account', read_only=True)
    
    class Meta:
        model = BalanceTransaction
        fields = [
            'id', 'user', 'user_account', 'transaction_type', 'debit', 'credit',
            'balance_before', 'balance_after', 'payment_transaction', 'voucher',
            'description', 'reference', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionQueueSerializer(serializers.ModelSerializer):
    user_account = serializers.CharField(source='user.account', read_only=True)
    
    class Meta:
        model = TransactionQueue
        fields = [
            'id', 'queue_type', 'user', 'user_account', 'method', 'initiator',
            'checkout_request_id', 'package_code', 'package', 'price', 'status',
            'account_reference', 'used_credit', 'failure_reason', 'error_code',
            'failure_category', 'retry_count', 'max_retries', 'last_retry_at',
            'priority', 'expires_at', 'pending_timeout_hours', 'gateway_result_data',
            'metadata', 'completed_at', 'failed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PointTransactionSerializer(serializers.ModelSerializer):
    user_account = serializers.CharField(source='user.account', read_only=True)
    
    class Meta:
        model = PointTransaction
        fields = [
            'id', 'user', 'user_account', 'transaction_type', 'points',
            'description', 'related_voucher', 'related_coupon', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
