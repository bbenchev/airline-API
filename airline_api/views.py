import json
import random
import string
import requests
from datetime import timedelta
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from django.views.decorators.csrf import csrf_exempt

def index(request):
    pass


def raise_error(reason):
  return HttpResponse(reason=reason, status=503, content_type='text/plain')


# For /api/findflight/
def find_flight(request):
    # Checks received data is correct
    if request.method != 'GET':
      return raise_error("Only GET requests are supported for this endpoint!")
    if request.content_type != 'application/json':
      return raise_error("Only JSON payloads are supported for this request!")

    payload = json.loads(request.body.decode('utf-8'))
    try:
      is_flex = payload["is_flex"]
      dep_airport = payload["dep_airport"]
      dest_airport = payload["dest_airport"]
      dep_date = payload["dep_date"]
    except KeyError:
      return raise_error("Invalid JSON keys! Check documentation!")

    if is_flex: # Figure out number of days from supplied date
        queryset = Flight.objects.filter(
            departure_airport__name__contains=dep_airport,
            destination_airport__name__contains=dest_airport
        )
    else:
        queryset = Flight.objects.filter(
            departure_time__contains=dep_date,
            departure_airport__name__contains=dep_airport,
            destination_airport__name__contains=dest_airport
        )

    if queryset.count() == 0:
        return raise_error("No available flights for the provided data")
    else: # Construct response
        response = {"flights": []}
        for flight in queryset:
            response["flights"].append(
                {
                  "flight_id":    str(flight.pk),
                  "flight_num":   flight.number,
                  "dep_airport":  flight.departure_airport.name,
                  "dest_airport": flight.destination_airport.name,
                  "dep_datetime": str(flight.departure_time),
                  "arr_datetime": str(flight.arrival_time),
                  "duration":     str(flight.duration),
                  "price":        flight.seat_price
                }
            )

        return JsonResponse(response)


# For /api/bookflight/
def book_flight(request):
    # Checks received data is correct
    if request.method != 'POST':
      return raise_error("Only POST requests are supported for this endpoint")
    if request.content_type != 'application/json':
      return raise_error("Only JSON payloads are supported for this request!")

    payload = json.loads(request.body.decode('utf-8'))
    try:
      flight_id = payload['flight_id']
      passengers = payload['passengers']
    except KeyError:
      return raise_error("Invalid JSON keys! Check documentation!")

    if len(passengers) == 0:
      return raise_error("You need to provide passengers in order to book a flight")


    DURATION_PERIOD = timedelta(minutes=5)
    # Create a booking
    booking_number = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    flight = Flight.objects.get(pk=flight_id)
    flight_capacity = flight.aircraft.seats
    number_of_seats = len(passengers)
    total_price = number_of_seats * flight.seat_price

    booking = Booking.objects.create(number=booking_number, flight=flight, number_of_seats=number_of_seats,
      status="ONHOLD", payment_window=DURATION_PERIOD)

    # Add passengers to booking and check if there are any seats left
    for each in passengers:
      passenger = Passenger.objects.create(first_name=each['first_name'], surname=each['surname'],
                  email=each['email'], phone=each["phone"])
      booking.passengers.add(passenger)

      flight_bookings = flight.booking_set.all()
      flight_seats_booked = 0
      for each in flight_bookings:
        flight_seats_booked += each.passengers.count()

      if flight_seats_booked > flight_capacity:
        booking.passengers.clear()
        booking.delete()
        return raise_error("No available seats for this flight")


    return JsonResponse({"booking_num": booking_number, "booking_status": "ONHOLD", "tot_price": total_price})


# For /api/paymentmethods/
def payment_methods(request):
    if request.method != 'GET':
      return raise_error("Only POST requests are supported for this endpoint")
    result = requests.get('http://directory.pythonanywhere.com/api/list/', json={"company_type": "payment"})

    if result.status_code == 200:
      try:
        companies = result.json()
      except ValueError:
        return raise_error("Invalid response from directory server!")

    companies_list = companies["company_list"]
    if len(companies_list) == 0:
      return raise_error("No payment providers")

    response = {"pay_providers": []}
    for each in companies_list:
      company = PaymentProvider.objects.filter(name=each["company_name"])
      response["pay_providers"].append(
        {"pay_provider_id": company[0].pk, "pay_provider_name": company[0].name}
      )

    return JsonResponse(response, status=201, reason="CREATED")


# For /api/payforbooking/
def pay_for_booking(request):
    # Checks received data is correct
    if request.method != 'POST':
      return raise_error("Only POST requests are supported for this endpoint")
    if request.content_type != 'application/json':
      return raise_error("Only JSON payloads are supported for this request!")


    data = json.loads(request.body.decode('utf-8'))

    try:
      booking_num = data['booking_num']
      payment_provider_id = data["pay_provider_id"]
    except KeyError:
      return raise_error("Invalid JSON keys! Check documentation!")

    # Get booking total cost
    booking = Booking.objects.get(number=booking_num)
    price = booking.number_of_seats * booking.flight.seat_price

    # Get details for payment provider
    provider = PaymentProvider.objects.get(pk=payment_provider_id)
    username = provider.username
    password = provider.password
    acc_num = provider.account_number

    request_body = {
      "account_num":    acc_num,
      "client_ref_num": booking_num,
      "amount":         str(price)
    }

    # Login to payment service provider and get invoice
    session = requests.Session()
    login_response = session.post(provider.address + "/api/login/", data={"username": username, "password": password})
    invoice_response = session.post(provider.address + "/api/createinvoice/", json=request_body)

    print(invoice_response)
    print(invoice_response.content)

    if invoice_response.status_code != 201:
      return raise_error("Bad response from payment provider")

    ref_id = invoice_response.json()['payprovider_ref_num']
    stamp = invoice_response.json()['stamp_code']
    booking.electronic_stamp = stamp
    booking.save()

    return JsonResponse(
      {
        "pay_provider_id": payment_provider_id,
        "invoice_id":      ref_id,
        "booking_num":     booking_num,
        "url":             provider.address
      },
      status=201,
      reason="CREATED"
    )


# For /api/finalizebooking
def finalize_booking(request):
    # Checks received data is correct
    if request.method != 'POST':
      return raise_error("Only POST requests are supported for this endpoint")
    if request.content_type != 'application/json':
      return raise_error("Only JSON payloads are supported for this request!")

    data = json.loads(request.body.decode('utf-8'))
    try:
      booking_num = data['booking_num']
      stamp = data["stamp"]
    except KeyError:
      return raise_error("Invalid JSON keys! Check documentation!")

    booking = Booking.objects.get(number=booking_num)

    if booking.electronic_stamp == stamp and booking.status == "ONHOLD":
      booking.status = "CONFIRMED"
      booking.save()
    else:
      return raise_error("Failed to confirm booking")

    return JsonResponse({"booking_num": booking_num, "booking_status": "CONFIRMED"}, status=201, reason="CREATED")


# For /api/bookingstatus/
def booking_status(request):
    if request.method != 'GET':
      return raise_error("Only GET requests are supported for this endpoint")
    if request.content_type != 'application/json':
      return raise_error("Only JSON payloads are supported for this request!")

    data = json.loads(request.body.decode('utf-8'))

    try:
      booking_num = data["booking_num"]
    except KeyError:
      return raise_error("Invalid JSON keys! Check documentation!")

    try:
      booking = Booking.objects.get(number=booking_num)
    except ObjectDoesNotExist:
      return raise_error("Invalid booking number!")

    return JsonResponse(
      {
        "booking_num":    booking_num,
        "booking_status": booking[0].status,
        "flight_num":     booking[0].flight.number,
        "dep_airport":    booking[0].flight.departure_airport.name,
        "dest_airport":   booking[0].flight.destination_airport.name,
        "dep_datetime":   str(booking[0].flight.departure_time),
        "arr_datetime":   str(booking[0].flight.arrival_time),
        "duration":       str(booking[0].flight.duration)
      }
    )

# For /api/cancelbooking/
def cancel_booking(request):
    if request.method != 'POST':
      return raise_error("Only POST requests are supported for this endpoint")
    if request.content_type != 'application/json':
      return raise_error("Only JSON payloads are supported for this request!")

    data = json.loads(request.body.decode('utf-8'))

    try:
      booking_num = data["booking_num"]
    except KeyError:
      return raise_error("Invalid JSON keys! Check documentation!")

    try:
      booking = Booking.objects.get(number=booking_num)
    except ObjectDoesNotExist:
      return raise_error("Invalid booking number!")

    if booking.status != "CANCELLED":
      booking.status = "CANCELLED"
      booking.save()

    return JsonResponse(
      {
        "booking_num":    booking_num,
        "booking_status": "CANCELLED"
      },
      status=201,
      reason="CREATED"
    )

