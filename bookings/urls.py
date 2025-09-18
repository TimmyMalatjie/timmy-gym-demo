# Create this file: bookings/urls.py

from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Public services catalog
    path('services/', views.services_list, name='services_list'),
    
    # Main booking interface (matches your actual view function)
    path('calendar/', views.booking_calendar, name='booking_calendar'),
    
    # Booking creation (using your class-based view)
    path('create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('success/', views.booking_success, name='booking_success'),
    
    # Booking management (matches your actual view functions)
    path('my-bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('<int:booking_id>/reschedule/', views.booking_reschedule, name='booking_reschedule'),
    
    # AJAX endpoints
    path('api/available-times/', views.get_available_times, name='get_available_times'),
]