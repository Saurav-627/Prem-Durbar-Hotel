from django.urls import path
from .views.public import DiningListView, DiningDetailView
from .views.ajax import book_table_ajax

app_name = 'dining'

urlpatterns = [
    path('', DiningListView.as_view(), name='dining_list'),
    path('<slug:slug>/', DiningDetailView.as_view(), name='dining_detail'),
    path('reserve/<int:venue_id>/', book_table_ajax, name='book_table_ajax'),
]
