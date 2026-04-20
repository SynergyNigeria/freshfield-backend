from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='total_invested',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='total_profit',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='portfolio_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=15),
        ),
    ]
