from django.urls import path
from .views import (
    CryptoListView, PortfolioView, BuyInvestmentView,
    SellInvestmentView, InvestmentHistoryView, MarketChartView, MarketTrackerView
)

app_name = 'investment'

urlpatterns = [
    path('cryptos/', CryptoListView.as_view(), name='crypto-list'),
    path('portfolio/', PortfolioView.as_view(), name='portfolio'),
    path('buy/', BuyInvestmentView.as_view(), name='buy'),
    path('sell/', SellInvestmentView.as_view(), name='sell'),
    path('history/', InvestmentHistoryView.as_view(), name='history'),
    path('market/btc/', MarketChartView.as_view(), {'symbol': 'bitcoin'}, name='market-btc'),
    path('market/tracker/', MarketTrackerView.as_view(), name='market-tracker'),
]
