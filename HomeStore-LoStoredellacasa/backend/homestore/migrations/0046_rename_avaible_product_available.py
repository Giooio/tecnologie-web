# Generated by Django 4.2.15 on 2024-12-09 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homestore', '0045_alter_product_stock'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='avaible',
            new_name='available',
        ),
    ]