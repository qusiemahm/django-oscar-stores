# Generated by Django 5.1.4 on 2025-02-23 12:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0011_alter_useraddress_options_and_more'),
        ('stores', '0015_alter_storeaddress_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storeaddress',
            name='country',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='address.country', verbose_name='Country'),
            preserve_default=False,
        ),
    ]
