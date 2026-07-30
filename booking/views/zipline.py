import datetime
from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Prefetch
from homepage.models.zipline_package import ZiplinePackage, ZiplinePackageBasePrice
from ..models.booking import Booking
from ..models.coupon import Coupon


@require_POST
def create_zipline_booking(request, package_id):
    """
    Handle Zipline adventure package booking creation with multi-currency rates,
    flight ticket counters, slot selection, and input validation.
    """
    selected_currency = request.COOKIES.get('currency', 'USD')
    package_qs = ZiplinePackage.objects.prefetch_related(
        Prefetch(
            'base_prices',
            queryset=ZiplinePackageBasePrice.objects.filter(currency__iso_code=selected_currency),
            to_attr='active_currency_price'
        )
    )
    package = get_object_or_404(package_qs, id=package_id, is_published=True)
    package.set_active_currency(selected_currency)

    name = (request.POST.get('name') or '').strip()
    email = (request.POST.get('email') or '').strip()
    phone = (request.POST.get('phone') or '').strip()
    no_of_flights_str = request.POST.get('no_of_flights', '1')
    flight_date_str = request.POST.get('flight_date')
    slot_time = request.POST.get('slot_time', 'Morning (09:00 AM - 12:00 PM)')
    promo_code = request.POST.get('promo_code', '').strip()
    special_requests = request.POST.get('special_requests', '')

    if not name or len(name) < 2:
        messages.error(request, "Please enter a valid guest name (at least 2 characters).")
        return redirect('homepage:home')

    if not email or '@' not in email or '.' not in email:
        messages.error(request, "Please enter a valid email address for ticket delivery.")
        return redirect('homepage:home')

    if not phone or len(phone) < 10:
        messages.error(request, "Please enter a valid contact phone number.")
        return redirect('homepage:home')

    try:
        no_of_flights = max(1, int(no_of_flights_str))
        flight_date = datetime.datetime.strptime(flight_date_str, "%Y-%m-%d").date() if flight_date_str else datetime.date.today()
    except (ValueError, TypeError):
        messages.error(request, "Invalid input details for Zipline booking.")
        return redirect('homepage:home')

    today_date = datetime.date.today()
    if flight_date < today_date:
        messages.error(request, "Flight date cannot be in the past. Please select today or a future date.")
        return redirect('homepage:home')

    unit_price = package.final_price or 0
    subtotal = unit_price * no_of_flights

    discount = Decimal('0.00')
    coupon = None
    if promo_code:
        coupon_obj = Coupon.objects.filter(code__iexact=promo_code, is_active=True).first()
        if coupon_obj:
            is_valid, err_msg = coupon_obj.is_valid(order_amount=subtotal, product_type='zipline', active_currency_code=selected_currency)
            if is_valid:
                coupon = coupon_obj
                discount = coupon_obj.calculate_discount(subtotal)
                messages.success(request, f"Promo code '{promo_code}' applied successfully!")
            else:
                messages.warning(request, f"Promo code '{promo_code}': {err_msg}")
        else:
            messages.warning(request, f"Invalid or expired promo code '{promo_code}'.")

    total = subtotal - discount

    booking = Booking.objects.create(
        booking_type='zipline',
        user=request.user if request.user.is_authenticated else None,
        zipline_package=package,
        guest_name=name,
        guest_email=email,
        guest_phone=phone,
        num_tickets=no_of_flights,
        flight_date=flight_date,
        slot_time=slot_time,
        subtotal=subtotal,
        currency_code=selected_currency,
        coupon=coupon,
        discount=discount,
        tax=Decimal('0.00'),
        total=total,
        special_requests=special_requests,
        status='draft'
    )

    # Track coupon redemption
    if coupon:
        coupon.redeem()

    return redirect('booking:checkout_page', booking_uid=booking.booking_uid)
