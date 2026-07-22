from django.urls import path
from .views import public

app_name = 'payments'

urlpatterns = [
    path('process/<uuid:booking_uid>/<str:gateway>/', public.process_payment, name='process_payment'),
    path('callback/<int:payment_id>/', public.payment_callback, name='payment_callback'),
    path('invoice/<uuid:booking_uid>/', public.view_invoice, name='view_invoice'),
]
