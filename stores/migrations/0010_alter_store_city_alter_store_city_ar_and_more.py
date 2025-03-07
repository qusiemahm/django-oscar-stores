# Generated by Django 5.1.4 on 2025-01-19 14:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0009_alter_store_state_alter_store_state_ar_and_more'),
        ('user', '0007_remove_city_name_ar_remove_city_name_en'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.city'),
        ),
        migrations.AlterField(
            model_name='store',
            name='city_ar',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.city'),
        ),
        migrations.AlterField(
            model_name='store',
            name='city_en',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.city'),
        ),
    ]
