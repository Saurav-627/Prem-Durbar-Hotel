from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.http import HttpResponse, Http404
from django.urls import reverse
from booking.models.booking import Booking
from ..models.payment import Payment
from ..services import get_processor_by_gateway_name
from ..services.base_payment import PaymentValidationResult
import uuid
import json
import logging

logger = logging.getLogger(__name__)

def process_payment(request, booking_uid, gateway):
    booking = get_object_or_404(Booking, booking_uid=booking_uid)
    
    if booking.status not in {'draft', 'pending'}:
        return HttpResponse("This booking has already been processed.")

    if gateway not in ['stripe', 'esewa', 'khalti']:
        raise Http404("Invalid payment gateway.")

    from ..models.payment_processor import PaymentProcessor
    from decimal import Decimal

    # Fetch payment processor metadata
    processor_meta = PaymentProcessor.objects.filter(code=gateway, is_published=True).first()

    taxable_amount = booking.subtotal - booking.discount
    tax_amount = Decimal('0.00')
    if processor_meta and processor_meta.apply_tax:
        tax_pct = Decimal(str(booking.room.tax_percentage or 0))
        tax_amount = taxable_amount * (tax_pct / Decimal('100.00'))
        booking.tax = tax_amount
        booking.total = taxable_amount + tax_amount
    else:
        booking.tax = Decimal('0.00')
        booking.total = taxable_amount
    booking.save(update_fields=['tax', 'total'])

    # Determine currency
    currency_obj = None
    if processor_meta:
        currency_obj = processor_meta.payment_currencies.first()
    if not currency_obj:
        # Fall back to the first currency price defined for the room
        first_cp = booking.room.base_prices.first()
        if first_cp:
            currency_obj = first_cp.currency

    # Create a pending Payment record with the correct amount and currency
    transaction_id = str(uuid.uuid4())
    payment = Payment.objects.create(
        booking=booking,
        gateway=gateway,
        currency=currency_obj,
        transaction_id=transaction_id,
        amount=booking.total,
        tax_amount=tax_amount,
        status='pending'
    )


    if gateway == 'stripe':
        # Keep simulated fallback for stripe
        context = {
            'booking': booking,
            'gateway': gateway,
            'payment': payment,
            'api_url': reverse('payments:payment_callback', args=[payment.id]),
            'form_method': 'GET',
            'form_data': {}
        }
        return render(request, 'payments/process.html', context)

    try:
        processor = get_processor_by_gateway_name(gateway)
        return_url = request.build_absolute_uri(reverse('payments:payment_callback', args=[payment.id]))

        kwargs = {
            'tax_amount': float(tax_amount)
        }

        if gateway == 'khalti':
            kwargs['display_name'] = f"Booking for {booking.room.title}"
            kwargs['customer_info'] = {
                'name': booking.guest_name,
                'email': booking.guest_email,
                'phone': booking.guest_phone,
            }
            from ..services.utils import to_minor_units
            kwargs['product_items'] = [{
                'identity': str(booking.room.id),
                'name': booking.room.title,
                'total_price': to_minor_units(booking.total),
                'quantity': 1,
                'unit_price': to_minor_units(booking.total)
            }]

        result = processor.initiate_payment(
            total_amount=float(booking.total),
            transaction_id=transaction_id,
            return_url=return_url,
            **kwargs
        )

        # Store initiation response or reference
        if gateway == 'khalti':
            payment.gateway_response = result.get('provider_reference')
            payment.save(update_fields=['gateway_response'])
        else:
            payment.gateway_response = json.dumps(result)
            payment.save(update_fields=['gateway_response'])

        context = {
            'booking': booking,
            'gateway': gateway,
            'payment': payment,
            'api_url': result['api_url'],
            'form_method': result['form_method'],
            'form_data': result['form_data']
        }
        return render(request, 'payments/process.html', context)

    except Exception as e:
        payment.status = 'failed'
        payment.gateway_response = str(e)
        payment.save()
        logger.error(f"Payment initiation failed for booking {booking_uid} via {gateway}: {e}")
        return HttpResponse(f"Payment initiation failed: {e}")

def payment_callback(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    booking = payment.booking

    if payment.status == 'success':
        return render(request, 'payments/success.html', {'booking': booking, 'payment': payment, 'message': "Payment already confirmed!"})

    gateway = payment.gateway

    if gateway == 'stripe':
        # Keep simulated success for stripe
        with transaction.atomic():
            from rooms.models.room import Room

            Room.objects.select_for_update().get(pk=booking.room_id)
            if not booking.has_room_availability():
                payment.status = 'failed'
                payment.gateway_response = 'Room inventory changed before confirmation.'
                payment.save(update_fields=['status', 'gateway_response'])
                booking.status = 'draft'
                booking.save(update_fields=['status'])

                message = 'Payment could not be confirmed because the room is no longer available. The booking remains a draft.'
                return render(request, 'payments/success.html', {'booking': booking, 'payment': payment, 'message': message})

            payment.status = 'success'
            payment.save(update_fields=['status'])
            booking.status = 'confirmed'
            booking.save(update_fields=['status'])

        message = f"Payment of {booking.currency_code} {payment.amount} successful via Stripe!"
        return render(request, 'payments/success.html', {'booking': booking, 'payment': payment, 'message': message})

    try:
        processor = get_processor_by_gateway_name(gateway)

        if gateway == 'khalti':
            pidx = request.GET.get('pidx') or payment.gateway_response
            if not pidx:
                raise ValueError("Khalti pidx transaction reference not found.")
            transaction_id = pidx
        elif gateway == 'esewa':
            transaction_id = payment.transaction_id
        else:
            raise ValueError(f"Unsupported callback gateway: {gateway}")

        validation_result = processor.validate_payment(
            total_amount=float(payment.amount),
            transaction_id=transaction_id
        )

        if validation_result.status == PaymentValidationResult.Status.SUCCESS:
            with transaction.atomic():
                from rooms.models.room import Room

                Room.objects.select_for_update().get(pk=booking.room_id)
                if not booking.has_room_availability():
                    payment.status = 'failed'
                    payment.gateway_response = 'Room inventory changed before confirmation.'
                    payment.save(update_fields=['status', 'gateway_response'])
                    booking.status = 'draft'
                    booking.save(update_fields=['status'])

                    return render(request, 'payments/success.html', {
                        'booking': booking,
                        'payment': payment,
                        'message': "Payment succeeded, but the room is no longer available. The booking remains a draft."
                    })

                payment.status = 'success'
                payment.gateway_response = json.dumps(dict(request.GET))
                payment.save(update_fields=['status', 'gateway_response'])
                booking.status = 'confirmed'
                booking.save(update_fields=['status'])

            message = f"Payment of {booking.currency_code} {payment.amount} successful via {gateway.upper()}!"
            return render(request, 'payments/success.html', {'booking': booking, 'payment': payment, 'message': message})

        elif validation_result.status == PaymentValidationResult.Status.PENDING:
            payment.status = 'pending'
            payment.save(update_fields=['status'])
            booking.status = 'draft'
            booking.save(update_fields=['status'])
            return render(request, 'payments/success.html', {
                'booking': booking,
                'payment': payment,
                'message': f"Payment is pending. Please verify with {gateway.upper()}. The booking is still a draft until payment completes."
            })
        else:
            payment.status = 'failed'
            payment.save(update_fields=['status'])
            booking.status = 'draft'
            booking.save(update_fields=['status'])

            return render(request, 'payments/success.html', {
                'booking': booking,
                'payment': payment,
                'message': f"Payment validation failed for {gateway.upper()}. The booking remains a draft."
            })

    except Exception as e:
        payment.status = 'failed'
        payment.save(update_fields=['status'])
        booking.status = 'draft'
        booking.save(update_fields=['status'])

        logger.error(f"Callback error for payment {payment_id}: {e}")
        return render(request, 'payments/success.html', {
            'booking': booking,
            'payment': payment,
            'message': f"Payment callback error: {e}"
        })

def view_invoice(request, booking_uid):
    from django.utils import timezone
    booking = get_object_or_404(Booking, booking_uid=booking_uid)
    booking.room.set_active_currency(booking.currency_code)
    payments = Payment.objects.filter(booking=booking, status='success')
    
    context = {
        'booking': booking,
        'payments': payments,
        'print_date': timezone.now(),
    }
    return render(request, 'admin_dashboard/bookings/invoice.html', context)

