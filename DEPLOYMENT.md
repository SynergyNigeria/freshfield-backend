# Backend Deployment Checklist

## Pre-Launch Checklist

### [ ] Environment Setup
- [ ] Copy `.env.example` to `.env`
- [ ] Update `SECRET_KEY` in `.env`
- [ ] Set `DEBUG = False` for production
- [ ] Verify `ALLOWED_HOSTS` configuration
- [ ] Setup database credentials if using PostgreSQL

### [ ] Database Setup
- [ ] Run `python manage.py makemigrations`
- [ ] Run `python manage.py migrate`
- [ ] Create superuser with `python manage.py createsuperuser`
- [ ] Verify database is accessible
- [ ] Add crypto assets through Django admin

### [ ] Static Files
- [ ] (Development) Static files are served automatically
- [ ] (Production) Run `python manage.py collectstatic --noinput`

### [ ] Security
- [ ] Verify `CORS_ALLOWED_ORIGINS` includes frontend URL
- [ ] Ensure token authentication is configured
- [ ] Review permission classes on all views
- [ ] Check CSRF settings for your deployment

### [ ] Testing
- [ ] Test user registration endpoint
- [ ] Test login endpoint
- [ ] Test wallet endpoints
- [ ] Test investment endpoints
- [ ] Verify authentication tokens work
- [ ] Test CORS headers

### [ ] Admin Panel
- [ ] Access `/admin/` and login
- [ ] Verify all models appear in admin
- [ ] Add test data (crypto assets, etc.)
- [ ] Test admin functionality

## Running Locally

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your settings

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver

# 8. Access at http://localhost:8000
# Admin at http://localhost:8000/admin/
```

## Testing Endpoints

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password2": "testpass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

### Get Wallet (use token from login)
```bash
curl -X GET http://localhost:8000/api/wallet/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Deposit
```bash
curl -X POST http://localhost:8000/api/wallet/deposit/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1000,
    "description": "Test deposit"
  }'
```

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Using Daphne (for WebSocket support)
```bash
pip install daphne
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Environment Variables for Production
```
SECRET_KEY=your-very-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=freshfield_db
DATABASE_USER=postgres
DATABASE_PASSWORD=your-secure-password
DATABASE_HOST=your-db-host
DATABASE_PORT=5432
```

## Monitoring

### View logs
```bash
python manage.py tail
```

### Database backups
```bash
python manage.py dumpdata > backup.json
```

## Troubleshooting

### Clear all data and reset
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Rebuild database (keep data)
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

### Check installed apps
```bash
python manage.py shell
from django.apps import apps
apps.get_app_configs()
```

## Notes

- All endpoints require token authentication except `/api/auth/register/` and `/api/auth/login/`
- Token authentication format: `Authorization: Token YOUR_TOKEN_HERE`
- Default token expiry is not set (configure as needed)
- CORS is enabled for `localhost:3000` by default
- Database defaults to SQLite (update for production)
