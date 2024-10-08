# Generated by Django 5.1.1 on 2024-10-01 09:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_customer_phone_number_alter_order_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='phone_number',
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 1, 9, 52, 42, 110306)),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('P', 'Paid'), ('U', 'Unpaid')], default='U', max_length=16),
        ),
        migrations.AlterField(
            model_name='product',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 1, 9, 52, 42, 109761)),
        ),
    ]
