# Generated by Django 4.2.15 on 2024-12-03 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homestore', '0036_orderitem_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sold_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
