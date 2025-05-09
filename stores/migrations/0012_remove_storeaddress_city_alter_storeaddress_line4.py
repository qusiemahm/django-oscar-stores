# Generated by Django 5.1.4 on 2025-01-20 07:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0011_storeaddress_city'),
        ('user', '0007_remove_city_name_ar_remove_city_name_en'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storeaddress',
            name='city',
        ),
        migrations.AlterField(
            model_name='storeaddress',
            name='line4',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.city', verbose_name='City'),
        ),
    ]
