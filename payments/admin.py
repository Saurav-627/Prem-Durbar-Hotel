from django.contrib import admin
from django.utils.html import format_html
from .models.payment import Payment
from .models.payment_processor import PaymentProcessor, PaymentProcessorCurrency

class PaymentProcessorCurrencyInline(admin.TabularInline):
    model = PaymentProcessorCurrency
    extra = 1

@admin.register(PaymentProcessor)
class PaymentProcessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'apply_tax', 'is_published')
    list_filter = ('apply_tax', 'is_published')
    search_fields = ('name', 'code')
    inlines = [PaymentProcessorCurrencyInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_booking', 'transaction_id', 'gateway', 'get_currency_iso', 'amount_ex_tax', 'tax_amount', 'status_badge', 'created_at')
    list_filter = ('gateway', 'status', 'created_at', 'currency')
    search_fields = ('transaction_id', 'booking__booking_uid', 'booking__guest_name')
    readonly_fields = ('created_at', 'updated_at')

    STATUS_STYLES = {
        'draft':    ('⚪', '#374151', '#f3f4f6'),   # gray
        'success':  ('🟢', '#14532d', '#bbf7d0'),   # green
        'pending':  ('🟡', '#713f12', '#fef9c3'),   # yellow
        'failed':   ('🔴', '#7f1d1d', '#fee2e2'),   # red
        'refunded': ('🔵', '#1e3a5f', '#dbeafe'),   # blue
    }

    @admin.display(description='Status')
    def status_badge(self, obj):
        icon, color, bg = self.STATUS_STYLES.get(
            obj.status, ('⚪', '#374151', '#f3f4f6')
        )
        return format_html(
            '<span style="'
            'display:inline-flex;align-items:center;gap:5px;'
            'padding:3px 10px;border-radius:999px;'
            'font-size:12px;font-weight:600;letter-spacing:0.4px;'
            'background:{};color:{};">'
            '{} {}</span>',
            bg, color, icon, obj.get_status_display()
        )

    @admin.display(description='Booking', ordering='booking')
    def get_booking(self, obj):
        label = str(obj.booking)
        truncated = (label[:28] + '…') if len(label) > 28 else label
        return format_html(
            '<span style="display:inline-block;max-width:200px;'
            'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'
            'vertical-align:middle;" title="{}">{}</span>',
            label, truncated
        )

    @admin.display(description='Currency')
    def get_currency_iso(self, obj):
        return obj.currency.iso_code if obj.currency else "-"

    @admin.display(description='Tax')
    def tax_amount(self, obj):
        currency = obj.currency.iso_code if obj.currency else (obj.booking.currency_code if obj.booking else '-')
        return f'{currency} {obj.tax_amount:.2f}'

    @admin.display(description='Amount', ordering='amount')
    def amount_ex_tax(self, obj):
        currency = obj.currency.iso_code if obj.currency else (obj.booking.currency_code if obj.booking else '-')
        amount = obj.amount_ex_tax if hasattr(obj, 'amount_ex_tax') else (obj.amount - obj.tax_amount)
        return f'{currency} {amount:.2f}'


