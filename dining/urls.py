from django.urls import path
from .views.public import DiningListView

app_name = 'dining'

urlpatterns = [
    path('', DiningListView.as_view(), name='dining_list'),
]
