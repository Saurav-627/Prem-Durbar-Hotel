from django.urls import path

from .views.public import AboutView, HomeView, SustainabilityView, ZiplineView

app_name = 'homepage'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('our-story/', AboutView.as_view(), name='our_story'),
    path('zipline/', ZiplineView.as_view(), name='zipline'),
    path('sustainability/', SustainabilityView.as_view(), name='sustainability'),
]
