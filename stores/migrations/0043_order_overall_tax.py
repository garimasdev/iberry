# Generated by Django 4.2.2 on 2024-08-26 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0042_outdoororder_overall_tax'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='overall_tax',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
