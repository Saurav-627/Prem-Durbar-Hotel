from django.urls import path
from .views.public import ContactView
from .views.ajax import submit_inquiry_ajax

app_name = 'contact'

urlpatterns = [
    path('', ContactView.as_view(), name='contact_page'),
    path('submit/', submit_inquiry_ajax, name='submit_inquiry_ajax'),
]
