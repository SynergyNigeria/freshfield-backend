from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from decimal import Decimal
import uuid
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer, DepositSerializer, WithdrawalSerializer

class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DepositSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            description = serializer.validated_data.get('description', 'Deposit')
            
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += amount
            wallet.save()
            
            transaction = Transaction.objects.create(
                wallet=wallet,
                transaction_type='DEPOSIT',
                amount=amount,
                status='COMPLETED',
                description=description,
                transaction_id=str(uuid.uuid4())
            )
            
            return Response({
                'transaction': TransactionSerializer(transaction).data,
                'new_balance': str(wallet.balance)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.profile.kyc_verified:
            return Response({
                'error': 'KYC_REQUIRED',
                'message': 'KYC verification is required before withdrawing funds.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = WithdrawalSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            if wallet.balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            
            wallet.balance -= amount
            wallet.save()
            
            vd = serializer.validated_data
            method = vd['method']
            if method == 'BANK':
                auto_desc = f"Bank: {vd['bank_name']} | Account: {vd['account_number']}"
            else:
                auto_desc = f"{vd['wallet_type']} Wallet: {vd['wallet_address']}"
            description = vd.get('description') or auto_desc

            transaction = Transaction.objects.create(
                wallet=wallet,
                transaction_type='WITHDRAWAL',
                amount=amount,
                status='COMPLETED',
                description=description,
                transaction_id=str(uuid.uuid4())
            )
            
            return Response({
                'transaction': TransactionSerializer(transaction).data,
                'new_balance': str(wallet.balance)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        transactions = wallet.transactions.all()[:50]
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
