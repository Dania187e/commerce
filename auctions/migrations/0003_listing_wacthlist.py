# Generated by Django 4.2.4 on 2023-08-29 19:57

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_rename_categoryname_category_category_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='wacthlist',
            field=models.ManyToManyField(blank=True, null=True, related_name='listingWacthlist', to=settings.AUTH_USER_MODEL),
        ),
    ]
