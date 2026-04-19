from django.contrib import admin
from .models import CryptoAsset, Portfolio, PortfolioHolding, Investment

# Portfolio stats are managed via the User admin page (users app).
# Only CryptoAsset is registered here for price/market data management.


@admin.register(CryptoAsset)
class CryptoAssetAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'current_price', 'market_cap', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['symbol', 'name']

