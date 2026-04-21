from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, KYCSubmission, UserNotification, FAQ, SupportTicket, SupportMessage

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'kyc_verified', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_staff', 'profile']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        email = validated_data.get('email')
        # Use email as username
        user = User.objects.create_user(username=email, **validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user)
        return user


class KYCSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCSubmission
        fields = ['id', 'id_document', 'selfie', 'status', 'admin_note', 'created_at', 'updated_at']
        read_only_fields = ['status', 'admin_note', 'created_at', 'updated_at']


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer']


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['id', 'email', 'subject', 'message', 'status', 'admin_reply', 'created_at']
        read_only_fields = ['status', 'admin_reply', 'created_at']


class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ['id', 'sender_is_admin', 'message', 'is_read', 'created_at']
