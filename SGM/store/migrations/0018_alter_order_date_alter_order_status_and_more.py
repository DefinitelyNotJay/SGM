# Generated by Django 5.0.6 on 2024-09-28 14:39

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_alter_order_date_alter_order_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 28, 21, 39, 33, 519085)),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('P', 'Paid'), ('U', 'Unpaid')], default='U', max_length=16),
        ),
        migrations.AlterField(
            model_name='product',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 28, 21, 39, 33, 509002)),
        ),
    ]
