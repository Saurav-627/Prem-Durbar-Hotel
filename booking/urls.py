from django.urls import path
from .views import booking

app_name = 'booking'

urlpatterns = [
    path('create/<int:room_id>/', booking.create_booking, name='create_booking'),
    path('checkout/<uuid:booking_uid>/', booking.checkout_page, name='checkout_page'),
    path('api/sync/', booking.channel_manager_sync, name='channel_manager_sync'),
]
