from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Custom Admin Dashboard
    path('admin/', include('admin_dashboard.urls', namespace='admin_dashboard')),
    
    # Native Django Admin (Developer fallback)
    path('django-admin/', admin.site.urls),
    
    # Modular Apps
    path('', include('homepage.urls', namespace='homepage')),
    path('rooms/', include('rooms.urls', namespace='rooms')),
    path('dining/', include('dining.urls', namespace='dining')),
    path('gallery/', include('gallery.urls', namespace='gallery')),
    path('booking/', include('booking.urls', namespace='booking')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('contact/', include('contact.urls', namespace='contact')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
