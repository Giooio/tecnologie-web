# Generated by Django 4.2.15 on 2024-09-03 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homestore', '0015_order_orderitem_remove_userpurchase_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='immagine',
            field=models.ImageField(upload_to='media/'),
        ),
    ]
