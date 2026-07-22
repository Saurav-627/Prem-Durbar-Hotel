from django.contrib import admin
from django.utils.html import format_html
from .models.coupon import Coupon
from .models.booking import Booking

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_spend', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_uid', 'guest_name', 'room', 'check_in', 'check_out', 'num_rooms', 'total', 'status_badge')
    list_filter = ('status', 'check_in', 'room')
    search_fields = ('booking_uid', 'guest_name', 'guest_email', 'guest_phone')
    readonly_fields = ('booking_uid', 'created_at', 'updated_at')
    list_select_related = ('room',)

    STATUS_STYLES = {
        'draft': ('⚪', '#374151', '#f3f4f6'),
        'pending': ('🟡', '#713f12', '#fef9c3'),
        'confirmed': ('🟢', '#14532d', '#bbf7d0'),
        'checked_in': ('🔵', '#1e3a5f', '#dbeafe'),
        'checked_out': ('✅', '#166534', '#dcfce7'),
        'cancelled': ('🔴', '#7f1d1d', '#fee2e2'),
    }

    @admin.display(description='Status')
    def status_badge(self, obj):
        icon, color, bg = self.STATUS_STYLES.get(obj.status, ('⚪', '#374151', '#f3f4f6'))
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:5px;'
            'padding:3px 10px;border-radius:999px;font-size:12px;'
            'font-weight:600;letter-spacing:0.4px;background:{};color:{};">'
            '{} {}</span>',
            bg, color, icon, obj.get_status_display()
        )
