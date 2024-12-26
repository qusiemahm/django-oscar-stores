# Generated by Django 5.1.4 on 2024-12-24 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0004_store_vendor_storestatus'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='store',
            options={'verbose_name': 'Branch', 'verbose_name_plural': 'Branches'},
        ),
        migrations.AlterField(
            model_name='openingperiod',
            name='weekday',
            field=models.PositiveIntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], verbose_name='Weekday'),
        ),
    ]
