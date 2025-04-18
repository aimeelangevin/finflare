# Generated by Django 5.2 on 2025-04-16 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finflare', '0006_aigeneratedtips'),
    ]

    operations = [
        migrations.AddField(
            model_name='spending',
            name='investment_type',
            field=models.CharField(blank=True, choices=[('groceries', 'Groceries'), ('entertainment', 'Entertainment'), ('utilities', 'Utilities'), ('dining', 'Dining'), ('transportation', 'Transportation')], max_length=50, null=True),
        ),
    ]
