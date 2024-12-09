# Generated by Django 4.2.15 on 2024-09-01 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homestore', '0004_remove_question_answered_at_useractivity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='immagine',
            field=models.ImageField(upload_to='products/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]