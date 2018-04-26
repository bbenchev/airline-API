# Generated by Django 2.0.2 on 2018-03-03 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('airline_api', '0002_auto_20180303_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10)),
                ('number_of_seats', models.IntegerField()),
                ('status', models.CharField(choices=[('ONHOLD', 'On Hold'), ('CONFIRMED', 'Confirmed'), ('CANCELLED', 'Cancelled'), ('TRAVELLED', 'Travelled')], max_length=15)),
                ('payment_window', models.DurationField()),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10)),
                ('departure_time', models.DateTimeField()),
                ('arrival_time', models.DateTimeField()),
                ('seat_price', models.FloatField()),
                ('aircraft', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline_api.Aircraft')),
                ('departure_airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departure', to='airline_api.Airport')),
                ('destination_airport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination', to='airline_api.Airport')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref_num', models.CharField(max_length=50)),
                ('amount', models.FloatField()),
                ('is_paid', models.BooleanField()),
                ('electronic_stamp', models.CharField(max_length=10)),
                ('booking_number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline_api.Booking')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentProvider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('address', models.URLField()),
                ('account_number', models.CharField(max_length=15)),
                ('username', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='flight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='airline_api.Flight'),
        ),
    ]