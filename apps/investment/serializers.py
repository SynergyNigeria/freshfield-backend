from rest_framework import serializers
from .models import CryptoAsset, Portfolio, PortfolioHolding, Investment

class CryptoAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoAsset
        fields = ['id', 'symbol', 'name', 'current_price', 'market_cap', 'updated_at']

class PortfolioHoldingSerializer(serializers.ModelSerializer):
    crypto = CryptoAssetSerializer(read_only=True)
    current_value = serializers.SerializerMethodField()

    def get_current_value(self, obj):
        return float(obj.quantity) * float(obj.crypto.current_price)

    class Meta:
        model = PortfolioHolding
        fields = ['id', 'crypto', 'quantity', 'average_cost', 'total_invested', 'current_value']

class PortfolioSerializer(serializers.ModelSerializer):
    holdings = PortfolioHoldingSerializer(many=True, read_only=True)
    total_value = serializers.SerializerMethodField()

    def get_total_value(self, obj):
        total = sum(float(h.quantity) * float(h.crypto.current_price) for h in obj.holdings.all())
        return total

    class Meta:
        model = Portfolio
        fields = [
            'id', 'holdings', 'total_value',
            'total_invested', 'total_profit', 'portfolio_amount', 'withdrawal_amount', 'withdrawal_note', 'admin_withdraw_note', 'kyc_note',
            'updated_at',
        ]

class InvestmentSerializer(serializers.ModelSerializer):
    crypto_symbol = serializers.CharField(source='crypto.symbol', read_only=True)

    class Meta:
        model = Investment
        fields = ['id', 'crypto_symbol', 'investment_type', 'quantity', 'unit_price', 'total_amount', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

class BuyInvestmentSerializer(serializers.Serializer):
    crypto_symbol = serializers.CharField(max_length=10)
    quantity = serializers.DecimalField(max_digits=15, decimal_places=8, min_value=0.00000001)

class SellInvestmentSerializer(serializers.Serializer):
    crypto_symbol = serializers.CharField(max_length=10)
    quantity = serializers.DecimalField(max_digits=15, decimal_places=8, min_value=0.00000001)
