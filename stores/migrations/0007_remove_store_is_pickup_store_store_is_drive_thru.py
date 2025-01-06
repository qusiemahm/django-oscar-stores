# Generated by Django 5.1.4 on 2024-12-31 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0006_store_city_ar_store_city_en_store_description_ar_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='is_pickup_store',
        ),
        migrations.AddField(
            model_name='store',
            name='is_drive_thru',
            field=models.BooleanField(default=False, verbose_name='Is Drive Trru'),
        ),
    ]
