from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from decimal import Decimal
import uuid
import requests
from datetime import datetime, timedelta
from .models import CryptoAsset, Portfolio, PortfolioHolding, Investment
from .serializers import (
    CryptoAssetSerializer, PortfolioSerializer, InvestmentSerializer,
    BuyInvestmentSerializer, SellInvestmentSerializer
)
from apps.wallet.models import Wallet, Transaction

class CryptoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cryptos = CryptoAsset.objects.all()
        serializer = CryptoAssetSerializer(cryptos, many=True)
        return Response(serializer.data)

class PortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data)

class BuyInvestmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BuyInvestmentSerializer(data=request.data)
        if serializer.is_valid():
            symbol = serializer.validated_data['crypto_symbol']
            quantity = serializer.validated_data['quantity']
            
            try:
                crypto = CryptoAsset.objects.get(symbol=symbol.upper())
            except CryptoAsset.DoesNotExist:
                return Response({'error': f'Crypto asset {symbol} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            total_cost = quantity * crypto.current_price
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            
            if wallet.balance < total_cost:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
            
            wallet.balance -= total_cost
            wallet.save()
            
            investment = Investment.objects.create(
                user=request.user,
                crypto=crypto,
                investment_type='BUY',
                quantity=quantity,
                unit_price=crypto.current_price,
                total_amount=total_cost,
                status='COMPLETED'
            )
            
            portfolio, _ = Portfolio.objects.get_or_create(user=request.user)
            holding, created = PortfolioHolding.objects.get_or_create(portfolio=portfolio, crypto=crypto)
            
            if not created:
                old_total = holding.total_invested
                old_quantity = holding.quantity
                holding.quantity = old_quantity + quantity
                holding.average_cost = (old_total + total_cost) / holding.quantity
                holding.total_invested = old_total + total_cost
            else:
                holding.quantity = quantity
                holding.average_cost = crypto.current_price
                holding.total_invested = total_cost
            
            holding.save()
            
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='BUY',
                amount=total_cost,
                status='COMPLETED',
                description=f'Bought {quantity} {symbol}',
                transaction_id=str(uuid.uuid4())
            )
            
            return Response({
                'investment': InvestmentSerializer(investment).data,
                'new_balance': str(wallet.balance)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SellInvestmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SellInvestmentSerializer(data=request.data)
        if serializer.is_valid():
            symbol = serializer.validated_data['crypto_symbol']
            quantity = serializer.validated_data['quantity']
            
            try:
                crypto = CryptoAsset.objects.get(symbol=symbol.upper())
            except CryptoAsset.DoesNotExist:
                return Response({'error': f'Crypto asset {symbol} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            portfolio = Portfolio.objects.filter(user=request.user).first()
            if not portfolio:
                return Response({'error': 'No portfolio found'}, status=status.HTTP_404_NOT_FOUND)
            
            holding = PortfolioHolding.objects.filter(portfolio=portfolio, crypto=crypto).first()
            if not holding or holding.quantity < quantity:
                return Response({'error': f'Insufficient {symbol} holdings'}, status=status.HTTP_400_BAD_REQUEST)
            
            total_revenue = quantity * crypto.current_price
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += total_revenue
            wallet.save()
            
            investment = Investment.objects.create(
                user=request.user,
                crypto=crypto,
                investment_type='SELL',
                quantity=quantity,
                unit_price=crypto.current_price,
                total_amount=total_revenue,
                status='COMPLETED'
            )
            
            holding.quantity -= quantity
            if holding.quantity == 0:
                holding.delete()
            else:
                holding.save()
            
            Transaction.objects.create(
                wallet=wallet,
                transaction_type='SELL',
                amount=total_revenue,
                status='COMPLETED',
                description=f'Sold {quantity} {symbol}',
                transaction_id=str(uuid.uuid4())
            )
            
            return Response({
                'investment': InvestmentSerializer(investment).data,
                'new_balance': str(wallet.balance)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestmentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        investments = Investment.objects.filter(user=request.user)[:50]
        serializer = InvestmentSerializer(investments, many=True)
        return Response(serializer.data)


class MarketChartView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, symbol='bitcoin'):
        """
        Fetch OHLC candlestick data from CoinGecko API.
        Returns Open, High, Low, Close data for proper candlestick visualization.
        """
        try:
            # Fetch OHLC data from CoinGecko
            url = f'https://api.coingecko.com/api/v3/coins/{symbol}/ohlc'
            params = {
                'vs_currency': 'usd',
                'days': '30',
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            ohlc_data = response.json()

            # CoinGecko returns: [[timestamp, open, high, low, close], ...]
            candles = []
            for entry in ohlc_data:
                if len(entry) >= 5:
                    timestamp, open_price, high_price, low_price, close_price = entry[0:5]
                    time = int(timestamp / 1000)  # Convert ms to seconds
                    
                    candle = {
                        'time': time,
                        'open': float(open_price),
                        'high': float(high_price),
                        'low': float(low_price),
                        'close': float(close_price),
                    }
                    candles.append(candle)

            return Response({
                'candles': candles,
                'live': True,
            })
        except requests.exceptions.RequestException as e:
            # Return mock OHLC data on error
            now = datetime.now()
            mock_candles = []
            for i in range(30):
                day = now - timedelta(days=30-i)
                timestamp = int(day.timestamp() * 1000)
                base_price = 66500 + (i * 100)
                variation = base_price * 0.03
                
                mock_candles.append({
                    'time': int(timestamp / 1000),
                    'open': base_price,
                    'high': base_price + variation,
                    'low': base_price - variation,
                    'close': base_price + (variation * 0.5),
                })
            return Response({
                'candles': mock_candles,
                'live': False,
            })
