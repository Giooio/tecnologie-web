# Generated by Django 4.2.15 on 2024-11-26 16:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homestore', '0017_cart_updated_at_cartitem_price_at_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='price_at_time',
        ),
    ]