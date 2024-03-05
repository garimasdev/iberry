# Generated by Django 4.2.2 on 2024-02-25 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0034_temporary_users_order_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporary_users',
            name='customer_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='temporary_users',
            name='customer_email',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='temporary_users',
            name='customer_name',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='temporary_users',
            name='customer_phone',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
