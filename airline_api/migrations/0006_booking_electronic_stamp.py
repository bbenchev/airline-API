# Generated by Django 2.0.2 on 2018-03-30 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airline_api', '0005_auto_20180328_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='electronic_stamp',
            field=models.CharField(default=None, max_length=15),
        ),
    ]
