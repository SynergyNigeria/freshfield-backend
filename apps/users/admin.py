from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from apps.wallet.models import Wallet
from apps.investment.models import Portfolio


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['phone', 'address', 'kyc_verified']


class WalletInline(admin.StackedInline):
    model = Wallet
    can_delete = False
    verbose_name_plural = 'Wallet Balance'
    fields = ['balance', 'currency']
    extra = 1
    max_num = 1


class PortfolioInline(admin.StackedInline):
    model = Portfolio
    can_delete = False
    verbose_name_plural = 'Portfolio Stats'
    fields = ['total_invested', 'total_profit', 'portfolio_amount']
    extra = 1
    max_num = 1


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline, WalletInline, PortfolioInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Ensure wallet and portfolio exist for every user
        Wallet.objects.get_or_create(user=obj)
        Portfolio.objects.get_or_create(user=obj)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'kyc_verified', 'created_at']
    list_filter = ['kyc_verified', 'created_at']
    search_fields = ['user__username', 'user__email']
