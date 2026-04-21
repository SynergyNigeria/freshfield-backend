from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class CryptoAsset(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # e.g., BTC
    name = models.CharField(max_length=50)  # e.g., Bitcoin
    current_price = models.DecimalField(max_digits=15, decimal_places=2)
    market_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = 'Crypto Asset'
        verbose_name_plural = 'Crypto Assets'

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
    # Admin-controlled summary stats
    total_invested = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    portfolio_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    withdrawal_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    withdrawal_note = models.TextField(
        blank=True,
        default='You are ineligible for withdrawal above $1000 at the moment',
    )
    kyc_note = models.TextField(
        blank=True,
        default='No KYC, no withdrawal.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Portfolio"

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

class PortfolioHolding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    crypto = models.ForeignKey(CryptoAsset, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=8)
    average_cost = models.DecimalField(max_digits=15, decimal_places=2)
    total_invested = models.DecimalField(max_digits=15, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.portfolio.user.username} - {self.crypto.symbol}: {self.quantity}"

    class Meta:
        verbose_name = 'Portfolio Holding'
        verbose_name_plural = 'Portfolio Holdings'
        unique_together = ('portfolio', 'crypto')

class Investment(models.Model):
    INVESTMENT_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    crypto = models.ForeignKey(CryptoAsset, on_delete=models.CASCADE)
    investment_type = models.CharField(max_length=10, choices=INVESTMENT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=15, decimal_places=8)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.investment_type} {self.quantity} {self.crypto.symbol}"

    class Meta:
        verbose_name = 'Investment'
        verbose_name_plural = 'Investments'
        ordering = ['-created_at']
