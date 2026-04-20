from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, KYCSubmission, UserNotification, FAQ, SupportTicket
from apps.wallet.models import Wallet, Transaction
from apps.investment.models import Portfolio


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['phone', 'address', 'kyc_verified']


class KYCSubmissionInline(admin.TabularInline):
    model = KYCSubmission
    extra = 0
    fields = ['id_document', 'selfie', 'status', 'admin_note', 'created_at']
    readonly_fields = ['created_at']


class UserNotificationInline(admin.TabularInline):
    model = UserNotification
    extra = 1
    fields = ['title', 'message', 'is_read', 'created_at']
    readonly_fields = ['created_at']


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
    inlines = [UserProfileInline, WalletInline, PortfolioInline, KYCSubmissionInline, UserNotificationInline]

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


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        profile, _ = UserProfile.objects.get_or_create(user=obj.user)
        profile.kyc_verified = obj.status == 'APPROVED'
        profile.save(update_fields=['kyc_verified'])


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'user__email', 'title']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'is_active', 'sort_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['question', 'answer']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'subject', 'message']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'status', 'transaction_id', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['wallet__user__username', 'wallet__user__email', 'transaction_id', 'description']
