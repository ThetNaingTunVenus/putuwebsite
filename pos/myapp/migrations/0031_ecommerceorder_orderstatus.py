# Generated by Django 5.0 on 2024-01-03 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0030_rename_ordered_by_ecommerceorder_customer_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecommerceorder',
            name='orderstatus',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
