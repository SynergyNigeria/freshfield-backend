from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE investment_portfolio ADD COLUMN IF NOT EXISTS total_invested NUMERIC(15,2) DEFAULT 0.00 NOT NULL;",
                "ALTER TABLE investment_portfolio ADD COLUMN IF NOT EXISTS total_profit NUMERIC(15,2) DEFAULT 0.00 NOT NULL;",
                "ALTER TABLE investment_portfolio ADD COLUMN IF NOT EXISTS portfolio_amount NUMERIC(15,2) DEFAULT 0.00 NOT NULL;",
            ],
            reverse_sql=[
                "ALTER TABLE investment_portfolio DROP COLUMN IF EXISTS total_invested;",
                "ALTER TABLE investment_portfolio DROP COLUMN IF EXISTS total_profit;",
                "ALTER TABLE investment_portfolio DROP COLUMN IF EXISTS portfolio_amount;",
            ],
            state_operations=[
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
            ],
        ),
    ]
