# Generated by Django 4.2.2 on 2024-10-10 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0043_order_overall_tax'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
