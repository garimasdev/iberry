# Generated by Django 4.2.2 on 2024-10-12 02:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0044_alter_price_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='temporary_users',
            name='customer_email',
        ),
    ]
