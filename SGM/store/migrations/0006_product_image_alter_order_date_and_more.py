# Generated by Django 5.1.1 on 2024-09-26 10:45

import datetime
import store.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_order_date_alter_product_add_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(default='default_image.png', upload_to=store.models.product_image_path),
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 26, 17, 45, 22, 944112)),
        ),
        migrations.AlterField(
            model_name='product',
            name='add_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 26, 17, 45, 22, 931715)),
        ),
    ]
