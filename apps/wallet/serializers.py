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
    method = serializers.ChoiceField(choices=['BANK', 'WALLET'])
    # Bank fields
    bank_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    account_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    # Wallet fields
    wallet_type = serializers.ChoiceField(choices=['TRC20', 'ERC20'], required=False, allow_null=True)
    wallet_address = serializers.CharField(max_length=200, required=False, allow_blank=True)
    description = serializers.CharField(max_length=200, required=False)

    def validate(self, data):
        method = data.get('method')
        if method == 'BANK':
            if not data.get('bank_name'):
                raise serializers.ValidationError({'bank_name': 'Bank name is required.'})
            if not data.get('account_number'):
                raise serializers.ValidationError({'account_number': 'Account number is required.'})
        elif method == 'WALLET':
            if not data.get('wallet_type'):
                raise serializers.ValidationError({'wallet_type': 'Wallet type is required.'})
            if not data.get('wallet_address'):
                raise serializers.ValidationError({'wallet_address': 'Wallet address is required.'})
        return data
