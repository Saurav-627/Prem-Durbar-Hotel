from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models.hotel_settings import HotelSettings
from .models.navigation import NavigationMenu
from .models.currency import Currency

@admin.register(HotelSettings)
class HotelSettingsAdmin(ModelAdmin):
    list_display = ('site_name', 'theme', 'contact_phone', 'contact_email')
    
    def has_add_permission(self, request):
        # Don't allow adding more than one settings entry (Singleton)
        return not HotelSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(NavigationMenu)
class NavigationMenuAdmin(ModelAdmin):
    list_display = ('name', 'url', 'position', 'order', 'parent', 'is_published')
    list_filter = ('position', 'parent', 'is_published')
    search_fields = ('name', 'url')
    list_editable = ('order', 'is_published')
    ordering = ('position', 'order')

@admin.register(Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ('iso_code', 'name', 'symbol', 'sequence', 'is_custom', 'is_published')
    list_filter = ('is_custom', 'is_published')
    search_fields = ('iso_code', 'name')
    list_editable = ('sequence', 'is_published')
