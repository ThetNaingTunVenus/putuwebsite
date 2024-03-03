# Generated by Django 5.0 on 2024-03-02 04:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0040_bestsellers_newarrival'),
    ]

    operations = [
        migrations.CreateModel(
            name='newestitem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.items')),
            ],
        ),
    ]
