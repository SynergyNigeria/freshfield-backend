from django.contrib import admin
from .models import Wallet, Transaction

# Wallet and Transaction are managed via the User admin page (users app).
# They are intentionally not registered here to keep the sidebar clean.

