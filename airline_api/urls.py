from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index),
    path('api/findflight/', views.find_flight),
    path('api/bookflight/', views.book_flight),
    path('api/paymentmethods/', views.payment_methods),
    path('api/payforbooking/', views.pay_for_booking),
    path('api/finalizebooking/', views.finalize_booking),
    path('api/bookingstatus/', views.booking_status),
    path('api/cancelbooking/', views.cancel_booking)
]