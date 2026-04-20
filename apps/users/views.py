from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.core.mail import send_mail
from .models import KYCSubmission, UserNotification, FAQ, SupportTicket
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    KYCSubmissionSerializer,
    UserNotificationSerializer,
    FAQSerializer,
    SupportTicketSerializer,
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


class SupportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        faqs = FAQ.objects.filter(is_active=True)
        return Response({'faq': FAQSerializer(faqs, many=True).data})

    def post(self, request):
        serializer = SupportTicketSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ticket = SupportTicket.objects.create(
            user=request.user,
            email=serializer.validated_data['email'],
            subject=serializer.validated_data['subject'],
            message=serializer.validated_data['message'],
        )

        mail_error = None
        try:
            send_mail(
                subject=f"[Support] {ticket.subject}",
                message=(
                    f"User: {request.user.email}\n"
                    f"Reply Email: {ticket.email}\n\n"
                    f"Message:\n{ticket.message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUPPORT_EMAIL],
                fail_silently=False,
            )
        except Exception as exc:
            mail_error = str(exc)

        data = SupportTicketSerializer(ticket).data
        data['mail_sent'] = mail_error is None
        if mail_error:
            data['mail_error'] = mail_error
        return Response(data, status=status.HTTP_201_CREATED)
