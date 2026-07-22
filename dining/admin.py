from django.contrib import admin
from .models.venue import DiningVenue
from .models.reservation import DiningReservation

@admin.register(DiningVenue)
class DiningVenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'timings', 'capacity', 'is_featured', 'is_published')
    list_filter = ('category', 'is_featured', 'is_published')
    list_editable = ('is_featured', 'is_published')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DiningReservation)
class DiningReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'date', 'time', 'guests', 'status')
    list_filter = ('status', 'date', 'venue')
    search_fields = ('name', 'email', 'phone')
