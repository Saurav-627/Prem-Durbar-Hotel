from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import ModelAdmin, TabularInline
from .models.room_category import RoomCategory
from .models.room import Room
from .models.room_image import RoomImage
from .models.room_facility import RoomFacility
from .models.room_seasonal_price import RoomSeasonalPrice
from .models.room_policy import RoomPolicy
from .models.room_availability import RoomAvailability

class RoomImageInline(TabularInline):
    model = RoomImage
    extra = 1

@admin.register(RoomCategory)
class RoomCategoryAdmin(ModelAdmin):
    list_display = ('name', 'total_rooms', 'slug', 'order', 'is_published')
    list_editable = ('total_rooms', 'order', 'is_published')
    prepopulated_fields = {'slug': ('name',)}

from .models.room_base_price import RoomBasePrice

class RoomBasePriceInline(TabularInline):
    model = RoomBasePrice
    extra = 2

class RoomPolicyInline(TabularInline):
    model = RoomPolicy
    extra = 1

class RoomPriceInline(TabularInline):
    model = RoomSeasonalPrice
    extra = 1

@admin.register(Room)
class RoomAdmin(ModelAdmin):
    list_display = ('title', 'category', 'base_price_display', 'tax_amount', 'price_with_tax_display', 'inventory_rooms', 'is_published', 'is_featured')
    list_filter = ('category', 'is_published', 'is_featured', 'facilities')
    search_fields = ('title', 'description', 'highlights')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [RoomBasePriceInline, RoomImageInline, RoomPolicyInline, RoomPriceInline]
    actions = ['duplicate_room']

    @admin.display(description='Prices')
    def base_price_display(self, obj):
        prices = obj.base_prices.all()
        if not prices:
            return "No prices defined"
        return ", ".join([f"{p.currency.iso_code} {p.base_price:.2f}" for p in prices])

    @admin.display(description='Tax')
    def tax_amount(self, obj):
        tax_pct = obj.tax_percentage or 0
        final_p = obj.final_price
        if final_p is None:
            return "N/A"
        amount = final_p * (tax_pct / 100)
        curr = obj.currency.iso_code if obj.currency else "N/A"
        return f'{curr} {amount:.2f}'

    @admin.display(description='Total Amount')
    def price_with_tax_display(self, obj):
        price = obj.price_with_tax
        if price is None:
            return "N/A"
        curr = obj.currency.iso_code if obj.currency else "N/A"
        return f'{curr} {price:.2f}'

    @admin.display(description='Rooms')
    def inventory_rooms(self, obj):
        return obj.total_rooms

    @admin.action(description='Duplicate selected rooms (Deep Copy)')
    def duplicate_room(self, request, queryset):
        import uuid
        count = 0
        for room in queryset:
            original_pk = room.pk
            original_room = Room.objects.get(pk=original_pk)

            room.pk = None
            room.title = f'{room.title} (Copy)'
            room.slug = f'{room.slug}-copy-{str(uuid.uuid4())[:8]}'
            room.save()

            room.facilities.set(original_room.facilities.all())

            for img in original_room.images.all():
                img.pk = None
                img.room = room
                img.save()

            for policy in original_room.policies.all():
                policy.pk = None
                policy.room = room
                policy.save()

            for price in original_room.seasonal_prices.all():
                price.pk = None
                price.room = room
                price.save()

            for cp in original_room.base_prices.all():
                cp.pk = None
                cp.room = room
                cp.save()

            count += 1

        self.message_user(request, f'Successfully duplicated {count} room(s).')

@admin.register(RoomFacility)
class RoomFacilityAdmin(ModelAdmin):
    list_display = ('name', 'icon_class', 'is_featured')
    search_fields = ('name',)

@admin.register(RoomSeasonalPrice)
class RoomPriceAdmin(ModelAdmin):
    list_display = ('room', 'name', 'start_date', 'end_date', 'price_override', 'is_active')
    list_filter = ('is_active', 'start_date', 'room')

@admin.register(RoomPolicy)
class RoomPolicyAdmin(ModelAdmin):
    list_display = ('title', 'room')
    list_filter = ('room',)

@admin.register(RoomAvailability)
class RoomAvailabilityAdmin(ModelAdmin):
    list_display = ('room', 'room_category', 'date', 'rooms_booked', 'is_available', 'booking_summary', 'booking_status')
    list_filter = ('is_available', 'date', 'room__category', 'room', 'booking__status')
    search_fields = ('room__title', 'room__category__name', 'booking__booking_uid', 'booking__guest_name', 'booking__guest_email')
    list_select_related = ('room', 'booking', 'room__category')

    @admin.display(description='Category', ordering='room__category__name')
    def room_category(self, obj):
        return obj.room.category.name if obj.room and obj.room.category else '-'

    @admin.display(description='Booking')
    def booking_summary(self, obj):
        if not obj.booking:
            return '-'
        return format_html(
            '<strong>{}</strong><br><span style="opacity:.75">{} · {}</span>',
            obj.booking.guest_name,
            obj.booking.booking_uid,
            obj.booking.payment_method,
        )

    @admin.display(description='Rooms Booked', ordering='rooms_booked')
    def rooms_booked(self, obj):
        return obj.rooms_booked if obj.booking else '-'

    @admin.display(description='Booking Status', ordering='booking__status')
    def booking_status(self, obj):
        if not obj.booking:
            return '-'
        icon = {
            'draft': '⚪',
            'pending': '🟡',
            'confirmed': '🟢',
            'checked_in': '🔵',
            'checked_out': '✅',
            'cancelled': '🔴',
        }.get(obj.booking.status, '⚪')
        return f'{icon} {obj.booking.get_status_display()}'
