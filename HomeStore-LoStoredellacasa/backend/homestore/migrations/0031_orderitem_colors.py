# Generated by Django 4.2.15 on 2024-12-02 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homestore', '0030_color_remove_product_colore_product_colori'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='colors',
            field=models.ManyToManyField(blank=True, to='homestore.color'),
        ),
    ]