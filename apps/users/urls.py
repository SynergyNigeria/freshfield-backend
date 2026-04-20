from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    ChangePasswordView,
    KYCView,
    NotificationListView,
    NotificationReadView,
    SupportView,
)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('kyc/', KYCView.as_view(), name='kyc'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('support/', SupportView.as_view(), name='support'),
]
