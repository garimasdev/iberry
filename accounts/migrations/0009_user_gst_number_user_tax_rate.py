# Generated by Django 4.2.2 on 2024-08-09 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_user_razorpay_clientid_user_razorpay_clientsecret'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gst_number',
            field=models.CharField(blank=True, help_text='GST Number', max_length=15, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='tax_rate',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Tax rate as a percentage', max_digits=5, null=True),
        ),
    ]