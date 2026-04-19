from django.urls import path
from .views import WalletView, DepositView, WithdrawalView, TransactionHistoryView

app_name = 'wallet'

urlpatterns = [
    path('', WalletView.as_view(), name='wallet'),
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdrawal/', WithdrawalView.as_view(), name='withdrawal'),
    path('transactions/', TransactionHistoryView.as_view(), name='transactions'),
]
