from rest_framework import serializers
from .models import Wallet, Transaction

class WalletSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'currency', 'created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'amount', 'status', 'description', 'transaction_id', 'created_at']
        read_only_fields = ['id', 'transaction_id', 'created_at']

class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=200, required=False)

class WithdrawalSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
    bank_account = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=200, required=False)
