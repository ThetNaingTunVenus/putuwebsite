# Generated by Django 5.0 on 2024-01-15 04:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0032_items_itm_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='messengerid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('m_status', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='messengerbot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=255)),
                ('status_id', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('messengerid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='myapp.messengerid')),
            ],
        ),
    ]
