import datetime
from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum, Prefetch
from rooms.models.room import Room
from rooms.models.room_availability import RoomAvailability
from rooms.models.room_base_price import RoomBasePrice
from ..models.booking import Booking
from ..models.coupon import Coupon


@require_POST
def create_booking(request, room_id):
    """
    Handle room chamber booking creation with multi-currency pricing,
    seasonal rate overrides, availability checks, and coupon discounts.
    """
    selected_currency = request.COOKIES.get('currency', 'USD')
    room_qs = Room.objects.prefetch_related(
        Prefetch(
            'base_prices',
            queryset=RoomBasePrice.objects.filter(currency__iso_code=selected_currency),
            to_attr='active_currency_price'
        )
    )
    room = get_object_or_404(room_qs, id=room_id, is_published=True)
    room.set_active_currency(selected_currency)
    
    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    phone = (request.POST.get('phone') or '').strip()
    check_in_str = request.POST.get('check_in')
    check_out_str = request.POST.get('check_out')
    adults_str = request.POST.get('adults', '2')
    children_str = request.POST.get('children', '0')
    promo_code = request.POST.get('promo_code', '').strip()
    special_requests = request.POST.get('special_requests', '')

    try:
        check_in = datetime.datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.datetime.strptime(check_out_str, "%Y-%m-%d").date()
        adults = int(adults_str)
        children = int(children_str)
        num_rooms = max(1, int(request.POST.get('num_rooms', '1')))
    except (ValueError, TypeError):
        messages.error(request, "Invalid input formats for reservation dates.")
        return redirect('rooms:room_detail', slug=room.slug)

    if check_out <= check_in:
        messages.error(request, "Check-out date must be after check-in date.")
        return redirect('rooms:room_detail', slug=room.slug)

    # Double check availability
    blocked = False
    available_rooms = room.total_rooms
    check_date = check_in
    while check_date < check_out:
        booked_count = RoomAvailability.objects.filter(room__category=room.category, date=check_date).aggregate(
            total=Sum('rooms_booked')
        )['total'] or 0
        remaining = room.total_rooms - booked_count
        if remaining < available_rooms:
            available_rooms = remaining
        if booked_count + num_rooms > room.total_rooms:
            blocked = True
        check_date += datetime.timedelta(days=1)

    if blocked:
        if available_rooms > 0:
            messages.error(request, f"Only {available_rooms} room{'s' if available_rooms != 1 else ''} available for the selected dates.")
        else:
            messages.error(request, "This room is not available for the selected dates. Please adjust your dates.")
        return redirect('rooms:room_detail', slug=room.slug)

    nights = (check_out - check_in).days
    daily_price = room.base_price
    
    # Seasonal price override
    seasonal = (
        room.seasonal_prices.filter(
            start_date__lte=check_out, end_date__gte=check_in, is_active=True,
            currency__iso_code=selected_currency
        ).order_by('-start_date').first()
        or room.seasonal_prices.filter(
            start_date__lte=check_out, end_date__gte=check_in, is_active=True,
            currency__isnull=True
        ).order_by('-start_date').first()
    )
    if seasonal:
        daily_price = seasonal.price_override

    subtotal = daily_price * nights * num_rooms
    
    # Process promo code
    discount = Decimal('0.00')
    coupon = None
    if promo_code:
        coupon_obj = Coupon.objects.filter(code__iexact=promo_code, is_active=True).first()
        if coupon_obj and coupon_obj.is_valid(subtotal):
            coupon = coupon_obj
            discount = coupon_obj.calculate_discount(subtotal)
            messages.success(request, f"Promo code '{promo_code}' applied successfully!")
        else:
            messages.warning(request, "Invalid or expired promo code.")

    taxable_amount = subtotal - discount
    tax = Decimal('0.00')
    total = taxable_amount

    booking = Booking.objects.create(
        booking_type='room',
        user=request.user if request.user.is_authenticated else None,
        room=room,
        guest_name=name,
        guest_email=email,
        guest_phone=phone,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        num_rooms=num_rooms,
        subtotal=subtotal,
        currency_code=selected_currency,
        coupon=coupon,
        discount=discount,
        tax=tax,
        total=total,
        special_requests=special_requests,
        status='draft'
    )

    return redirect('booking:checkout_page', booking_uid=booking.booking_uid)
