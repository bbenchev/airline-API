from django.db import models
from django import forms
import pytz

class Aircraft(models.Model):
    aircraft_type = models.CharField(max_length=20)
    reg_number = models.CharField(max_length=10)
    seats = models.IntegerField()

    def __str__(self):
        return self.aircraft_type


class Airport(models.Model):
    choices = []
    for timezone in pytz.all_timezones:
        choices.append((timezone, timezone))

    name = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    time_zone = models.CharField(max_length=50, choices=choices, default=choices[-5])

    def __str__(self):
        return self.name

class Flight(models.Model):
    number = models.CharField(max_length=10)
    departure_airport = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name="departure")
    destination_airport = models.ForeignKey("Airport", on_delete=models.CASCADE, related_name="destination")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    @property
    def duration(self):
        return self.arrival_time - self.departure_time

    aircraft = models.ForeignKey("Aircraft", on_delete=models.CASCADE)
    seat_price = models.FloatField()

    def __str__(self):
        return self.number

class Passenger(models.Model):
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)

    def __str__(self):
        return self.first_name + " " + self.surname

class Booking(models.Model):
    STATUSES = [
        ("ONHOLD", "On Hold"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("TRAVELLED", "Travelled")
    ]

    number = models.CharField(max_length=10)
    flight = models.ForeignKey("Flight", on_delete=models.CASCADE)
    passengers = models.ManyToManyField("Passenger", related_name="bookings")
    number_of_seats = models.IntegerField()
    status = models.CharField(max_length=15, choices=STATUSES)
    payment_window = models.DurationField()
    electronic_stamp = models.CharField(max_length=15)

    def __str__(self):
        return self.number


class PaymentProvider(models.Model):
    name = models.CharField(max_length=50)
    address = models.URLField()
    account_number = models.CharField(max_length=15)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    ref_num_airline = models.CharField(max_length=50)
    ref_num_payment = models.CharField(max_length=50, default=None) #reference from the payment service db
    booking_number = models.CharField(max_length=10) # booking_number = models.ForeignKey("Booking", on_delete=models.CASCADE)
    amount = models.FloatField()
    is_paid = models.BooleanField()
    electronic_stamp = models.CharField(max_length=10) #To be deleted before sending to client

    def __str__(self):
        return self.ref_num



