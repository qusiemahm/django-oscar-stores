# Generated by Django 4.2.16 on 2024-11-11 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_rename_created_at_vendor_registration_date_and_more'),
        ('stores', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='city',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='store',
            name='is_main',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='store',
            name='state',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='store',
            name='vendor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='vendor.vendor'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='openingperiod',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='openingperiod',
            name='weekday',
            field=models.PositiveIntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday'), (8, 'Public Holidays')], verbose_name='Weekday'),
        ),
        migrations.AlterField(
            model_name='store',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='storeaddress',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='storeaddress',
            name='store',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='address', to='stores.store', verbose_name='Store'),
        ),
        migrations.AlterField(
            model_name='storegroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='storestock',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]