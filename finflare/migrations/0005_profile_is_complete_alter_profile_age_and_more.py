# Generated by Django 4.2.20 on 2025-03-25 17:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("finflare", "0004_rename_name_investments_investment_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="is_complete",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="profile",
            name="age",
            field=models.IntegerField(
                blank=True,
                null=True,
                validators=[django.core.validators.MinValueValidator(18)],
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="current_employment",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="income",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10000000000, null=True
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="name",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="retirement_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="savings",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=100000000000, null=True
            ),
        ),
    ]
