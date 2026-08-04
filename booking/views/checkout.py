from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from rooms.models.room_base_price import RoomBasePrice
from homepage.models.zipline_package import ZiplinePackageBasePrice
from ..models.booking import Booking


def checkout_page(request, booking_uid):
    """
    Render checkout page for guest payment initiation (supports both Room and Zipline bookings).
    """
    selected_currency = request.COOKIES.get('currency', 'USD')
    
    booking_qs = Booking.objects.prefetch_related(
        Prefetch(
            'room__base_prices',
            queryset=RoomBasePrice.objects.filter(currency__iso_code=selected_currency),
            to_attr='active_currency_price'
        ),
        Prefetch(
            'zipline_package__base_prices',
            queryset=ZiplinePackageBasePrice.objects.filter(currency__iso_code=selected_currency),
            to_attr='active_currency_price'
        )
    )
    booking = get_object_or_404(booking_qs, booking_uid=booking_uid)
    if booking.booking_type == 'room' and booking.room:
        booking.room.set_active_currency(selected_currency)
        if booking.room.tax_percentage and booking.status == 'draft':
            tax_pct = Decimal(str(booking.room.tax_percentage))
            taxable_amount = booking.subtotal - booking.discount
            calculated_tax = (taxable_amount * (tax_pct / Decimal('100.00'))).quantize(Decimal('0.01'))
            calculated_total = taxable_amount + calculated_tax
            if booking.tax != calculated_tax or booking.total != calculated_total:
                booking.tax = calculated_tax
                booking.total = calculated_total
                booking.save(update_fields=['tax', 'total'])
    elif booking.booking_type == 'zipline' and booking.zipline_package:
        booking.zipline_package.set_active_currency(selected_currency)
    
    return render(request, 'booking/checkout.html', {'booking': booking})
