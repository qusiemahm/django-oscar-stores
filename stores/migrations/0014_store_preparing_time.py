# Generated by Django 5.1.4 on 2025-02-12 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0013_alter_store_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='preparing_time',
            field=models.PositiveIntegerField(default=30, help_text='Estimated time (in minutes) required for order preparation', verbose_name='Preparing Time (minutes)'),
        ),
    ]
