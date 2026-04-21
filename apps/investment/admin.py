from django.contrib import admin
from .models import CryptoAsset, Portfolio, PortfolioHolding, Investment


@admin.register(CryptoAsset)
class CryptoAssetAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'current_price', 'market_cap', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['symbol', 'name']


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_invested', 'portfolio_amount', 'withdrawal_amount', 'updated_at']
    search_fields = ['user__username', 'user__email']
    fields = ['user', 'total_invested', 'portfolio_amount', 'total_profit', 'withdrawal_amount', 'withdrawal_note', 'kyc_note']

