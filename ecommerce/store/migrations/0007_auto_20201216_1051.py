# Generated by Django 3.1.4 on 2020-12-16 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20201216_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='address',
            field=models.CharField(default=None, max_length=200),
        ),
    ]