# Generated by Django 2.0.2 on 2018-03-30 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airline_api', '0007_auto_20180330_2110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='electronic_stamp',
            field=models.CharField(default='0', max_length=15),
        ),
    ]
