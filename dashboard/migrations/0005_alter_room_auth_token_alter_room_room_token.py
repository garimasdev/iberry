# Generated by Django 4.2.2 on 2023-06-10 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_alter_room_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='auth_token',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_token',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
