from django.urls import path

from .views.ajax import submit_inquiry_ajax
from .views.public import ContactView, subscribe_newsletter, verify_newsletter

app_name = 'contact'

urlpatterns = [
    path('', ContactView.as_view(), name='contact_page'),
    path('submit/', submit_inquiry_ajax, name='submit_inquiry_ajax'),
    path('newsletter/subscribe/', subscribe_newsletter, name='subscribe_newsletter'),
    path('newsletter/verify/<str:token>/', verify_newsletter, name='verify_newsletter'),
]
