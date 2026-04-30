from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import KYCSubmission, UserNotification, FAQ, SupportTicket, SupportMessage
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    KYCSubmissionSerializer,
    UserNotificationSerializer,
    FAQSerializer,
    SupportTicketSerializer,
    SupportMessageSerializer,
)

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class MigrationCheckView(APIView):
    """MVP migration flow: check if account exists and still needs initial password setup."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email).first()
        can_setup = bool(user and not user.has_usable_password())
        return Response({'can_setup_password': can_setup})


class MigrationSetPasswordView(APIView):
    """MVP migration flow: set password for migrated users created without a usable password."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password')
        password2 = request.data.get('password2')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not password or not password2:
            return Response({'error': 'Both password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if password != password2:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({'error': 'Account not eligible for migration setup.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.has_usable_password():
            return Response({'error': 'This account already has a password. Please use normal login.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(password, user=user)
        except ValidationError as exc:
            return Response({'error': ' '.join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save(update_fields=['password'])

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Password set successfully. You can now sign in.',
            'user': UserSerializer(user).data,
            'token': token.key,
        })

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.save()
        
        profile = user.profile
        profile.phone = request.data.get('phone', profile.phone)
        profile.address = request.data.get('address', profile.address)
        profile.save()
        
        return Response(UserSerializer(user).data)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        # Verify current password
        if not user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify new passwords match
        if new_password != confirm_password:
            return Response(
                {'error': 'New passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check password length
        if len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters long'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update password
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password changed successfully'})


class KYCView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        submission = KYCSubmission.objects.filter(user=request.user).first()
        if not submission:
            return Response({
                'has_kyc': False,
                'kyc_verified': request.user.profile.kyc_verified,
                'message': 'No KYC submission yet. Upload your ID and selfie to continue.'
            })

        return Response({
            'has_kyc': True,
            'kyc_verified': request.user.profile.kyc_verified,
            'submission': KYCSubmissionSerializer(submission).data,
        })

    def post(self, request):
        existing = KYCSubmission.objects.filter(user=request.user).first()
        if existing and existing.status in ('PENDING', 'APPROVED'):
            return Response({
                'error': 'SUBMISSION_EXISTS',
                'message': (
                    'Your KYC is already under review.' if existing.status == 'PENDING'
                    else 'Your KYC has already been approved.'
                ),
                'status': existing.status,
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = KYCSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        KYCSubmission.objects.create(
            user=request.user,
            id_document=serializer.validated_data['id_document'],
            selfie=serializer.validated_data['selfie'],
        )

        profile = request.user.profile
        profile.kyc_verified = False
        profile.save(update_fields=['kyc_verified'])

        UserNotification.objects.create(
            user=request.user,
            title='KYC Submitted',
            message='Your KYC documents were submitted successfully and are awaiting review.'
        )

        latest = KYCSubmission.objects.filter(user=request.user).first()
        return Response(KYCSubmissionSerializer(latest).data, status=status.HTTP_201_CREATED)


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = UserNotification.objects.filter(user=request.user)[:100]
        return Response(UserNotificationSerializer(notifications, many=True).data)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        notification = UserNotification.objects.filter(user=request.user, id=notification_id).first()
        if not notification:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'message': 'Notification marked as read'})


class SupportChatView(APIView):
    """User: GET own messages, POST new message. Admin: GET list of chat threads."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            # Return list of unique users who have sent messages
            from django.db.models import Max, Count, Q
            threads = (
                SupportMessage.objects
                .values('user')
                .annotate(
                    last_at=Max('created_at'),
                    unread=Count('id', filter=Q(is_read=False, sender_is_admin=False)),
                )
                .order_by('-last_at')
            )
            result = []
            for t in threads:
                u = User.objects.get(pk=t['user'])
                last_msg = SupportMessage.objects.filter(user=u).order_by('-created_at').first()
                result.append({
                    'user_id': u.id,
                    'username': u.username,
                    'email': u.email,
                    'unread': t['unread'],
                    'last_message': last_msg.message[:80] if last_msg else '',
                    'last_at': last_msg.created_at if last_msg else None,
                })
            return Response(result)
        else:
            # Mark admin messages as read for this user
            SupportMessage.objects.filter(user=request.user, sender_is_admin=True, is_read=False).update(is_read=True)
            msgs = SupportMessage.objects.filter(user=request.user)
            return Response(SupportMessageSerializer(msgs, many=True).data)

    def post(self, request):
        if request.user.is_staff:
            return Response({'error': 'Admin must reply via /support/<user_id>/reply/'}, status=status.HTTP_400_BAD_REQUEST)
        msg_text = request.data.get('message', '').strip()
        if not msg_text:
            return Response({'error': 'Message cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
        msg = SupportMessage.objects.create(
            user=request.user,
            sender_is_admin=False,
            message=msg_text,
        )
        return Response(SupportMessageSerializer(msg).data, status=status.HTTP_201_CREATED)


class SupportUnreadView(APIView):
    """Returns the number of unread messages for the current user (admin msgs unread)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = SupportMessage.objects.filter(
            user=request.user,
            sender_is_admin=True,
            is_read=False,
        ).count()
        return Response({'unread': count})


class AdminSupportReplyView(APIView):
    """Admin only: GET all messages for a user, POST a reply."""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        target = User.objects.filter(pk=user_id).first()
        if not target:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        # Mark user messages as read for admin
        SupportMessage.objects.filter(user=target, sender_is_admin=False, is_read=False).update(is_read=True)
        msgs = SupportMessage.objects.filter(user=target)
        return Response(SupportMessageSerializer(msgs, many=True).data)

    def post(self, request, user_id):
        if not request.user.is_staff:
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        target = User.objects.filter(pk=user_id).first()
        if not target:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        msg_text = request.data.get('message', '').strip()
        if not msg_text:
            return Response({'error': 'Message cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
        msg = SupportMessage.objects.create(
            user=target,
            sender_is_admin=True,
            message=msg_text,
        )
        return Response(SupportMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
