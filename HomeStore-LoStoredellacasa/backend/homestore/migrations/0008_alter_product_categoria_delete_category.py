# Generated by Django 4.2.15 on 2024-09-01 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homestore', '0007_alter_product_categoria'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='categoria',
            field=models.CharField(max_length=200),
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
