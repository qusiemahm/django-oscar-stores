# Generated by Django 5.1.4 on 2025-01-20 06:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0010_alter_store_city_alter_store_city_ar_and_more'),
        ('user', '0007_remove_city_name_ar_remove_city_name_en'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeaddress',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.city'),
        ),
    ]
