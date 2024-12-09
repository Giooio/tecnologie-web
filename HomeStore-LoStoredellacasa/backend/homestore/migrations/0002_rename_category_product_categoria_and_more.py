# Generated by Django 4.2.15 on 2024-08-09 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homestore', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='category',
            new_name='categoria',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='description',
            new_name='descrizione',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='image',
            new_name='immagine',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='name',
            new_name='nome',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='price',
            new_name='prezzo',
        ),
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
    ]