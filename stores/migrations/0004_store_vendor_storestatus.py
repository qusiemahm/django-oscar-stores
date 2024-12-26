# Generated by Django 5.1.4 on 2024-12-22 13:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0003_remove_store_vendor'),
        ('vendor', '0004_delete_vendorpermissionplaceholder'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='vendor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='vendor.vendor'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='StoreStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('busy', 'Busy')], max_length=10)),
                ('duration', models.DurationField(blank=True, help_text='Duration for which the status is active', null=True)),
                ('set_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='stores.store')),
            ],
            options={
                'verbose_name': 'Store Status',
                'verbose_name_plural': 'Store Statuses',
                'ordering': ['-set_at'],
            },
        ),
    ]