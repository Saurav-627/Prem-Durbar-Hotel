from django.urls import path
from . import views

app_name = 'booking'

urlpatterns = [
    path('create/<int:room_id>/', views.create_booking, name='create_booking'),
    path('zipline/create/<int:package_id>/', views.create_zipline_booking, name='create_zipline_booking'),
    path('checkout/<uuid:booking_uid>/', views.checkout_page, name='checkout_page'),
    path('api/sync/', views.channel_manager_sync, name='channel_manager_sync'),
]
