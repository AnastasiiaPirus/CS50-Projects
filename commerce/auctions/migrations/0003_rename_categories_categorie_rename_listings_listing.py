# Generated by Django 4.1.2 on 2022-11-30 00:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_categories_listings'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Categories',
            new_name='Categorie',
        ),
        migrations.RenameModel(
            old_name='Listings',
            new_name='Listing',
        ),
    ]