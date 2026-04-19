# Freshfield Investment App - Backend

A Django REST API for a mini investment application with crypto trading features.

## Features

- User authentication (register, login)
- Wallet management (deposit, withdrawal)
- Crypto portfolio management
- Buy/Sell BTC transactions
- Transaction history

## Project Structure

```
backend/
├── config/              # Django configuration
│   ├── settings.py      # Project settings
│   ├── urls.py          # URL routing
│   ├── wsgi.py          # WSGI config
│   └── asgi.py          # ASGI config
├── apps/
│   ├── users/           # User authentication & profiles
│   ├── wallet/          # Wallet & transaction management
│   └── investment/      # Investment & portfolio management
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── .env.example        # Environment variables template
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

```bash
# Copy .env.example to .env
cp .env.example .env

# Update .env with your configuration
```

### 4. Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile

### Wallet
- `GET /api/wallet/` - Get wallet info
- `POST /api/wallet/deposit/` - Deposit funds
- `POST /api/wallet/withdrawal/` - Withdraw funds
- `GET /api/wallet/transactions/` - Get transaction history

### Investment
- `GET /api/investment/cryptos/` - List available crypto assets
- `GET /api/investment/portfolio/` - Get user portfolio
- `POST /api/investment/buy/` - Buy crypto
- `POST /api/investment/sell/` - Sell crypto
- `GET /api/investment/history/` - Get investment history

## Admin Panel

Access Django admin at: `http://localhost:8000/admin/`

## Technologies Used

- Django 4.2.11
- Django REST Framework 3.14.0
- SQLite (default for development)
- Token Authentication

## Environment Variables

See `.env.example` for all available configuration options.

## Notes

- Uses SQLite for simple development setup
- CORS is configured to allow requests from `http://localhost:3000` (frontend)
- Token authentication is required for all protected endpoints
- No external services required (Celery, Redis) - simple MVP only
