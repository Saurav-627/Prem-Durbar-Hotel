from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.http import HttpResponse, Http404, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from booking.models.booking import Booking
from ..models.payment import Payment
from ..services import get_processor_by_gateway_name
from ..services.base_payment import PaymentValidationResult
import uuid
import json
import logging
import stripe

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
    if processor_meta and processor_meta.apply_tax and booking.room:
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
        if booking.room:
            first_cp = booking.room.base_prices.first()
            if first_cp:
                currency_obj = first_cp.currency
        elif booking.zipline_package:
            first_cp = booking.zipline_package.base_prices.first()
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
        try:
            processor = get_processor_by_gateway_name('stripe')
            return_url = request.build_absolute_uri(reverse('payments:payment_callback', args=[payment.id]))
            item_name = booking.room.title if booking.room else (booking.zipline_package.name if booking.zipline_package else "Resort Booking")
            
            result = processor.initiate_payment(
                total_amount=float(booking.total),
                transaction_id=transaction_id,
                return_url=return_url,
                cancel_url=request.build_absolute_uri(reverse('booking:checkout_page', args=[booking.booking_uid])),
                currency=booking.currency_code.lower(),
                display_name=f"Booking for {item_name}",
                customer_info={
                    'name': booking.guest_name,
                    'email': booking.guest_email,
                    'phone': booking.guest_phone,
                },
                booking_uid=booking.booking_uid,
                payment_id=payment.id
            )
            
            payment.gateway_response = json.dumps(result)
            payment.save(update_fields=['gateway_response'])

            return redirect(result['api_url'])
        except Exception as e:
            payment.status = 'failed'
            payment.gateway_response = str(e)
            payment.save()
            logger.error(f"Stripe payment initiation failed for booking {booking_uid}: {e}")
            return HttpResponse(f"Stripe payment initiation failed: {e}")

    try:
        processor = get_processor_by_gateway_name(gateway)
        return_url = request.build_absolute_uri(reverse('payments:payment_callback', args=[payment.id]))

        kwargs = {
            'tax_amount': float(tax_amount)
        }

        if gateway == 'khalti':
            item_name = booking.room.title if booking.room else (booking.zipline_package.name if booking.zipline_package else "Booking")
            # pyrefly: ignore [bad-assignment]
            kwargs['display_name'] = f"Booking for {item_name}"
            # pyrefly: ignore [bad-assignment]
            kwargs['customer_info'] = {
                'name': booking.guest_name,
                'email': booking.guest_email,
                'phone': booking.guest_phone,
            }
            from ..services.utils import to_minor_units
            # pyrefly: ignore [bad-assignment]
            kwargs['product_items'] = [{
                'identity': str(booking.room.id if booking.room else (booking.zipline_package.id if booking.zipline_package else 1)),
                'name': item_name,
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
        session_id = request.GET.get('session_id')
        if session_id:
            try:
                processor = get_processor_by_gateway_name('stripe')
                validation_result = processor.validate_payment(
                    total_amount=float(payment.amount),
                    # pyrefly: ignore [bad-argument-type]
                    transaction_id=payment.transaction_id,
                    session_id=session_id
                )
                if validation_result.status == PaymentValidationResult.Status.SUCCESS:
                    with transaction.atomic():
                        if booking.room_id:
                            from rooms.models.room import Room
                            Room.objects.select_for_update().get(pk=booking.room_id)

                        if booking.has_room_availability():
                            payment.status = 'success'
                            payment.gateway_response = json.dumps(validation_result.details or {})
                            payment.save(update_fields=['status', 'gateway_response'])
                            booking.status = 'confirmed'
                            booking.save(update_fields=['status'])
                            message = f"Payment of {booking.currency_code} {payment.amount} successful via STRIPE!"
                        else:
                            payment.status = 'failed'
                            payment.gateway_response = 'Room inventory changed before confirmation.'
                            payment.save(update_fields=['status', 'gateway_response'])
                            message = "Payment succeeded, but the room is no longer available. The booking remains a draft."
                else:
                    payment.status = 'failed'
                    payment.save(update_fields=['status'])
                    message = f"Stripe payment failed: {validation_result.message}"
            except Exception as e:
                logger.error(f"Stripe validation exception: {e}")
                message = f"Stripe validation error: {e}"
        else:
            message = "Stripe session reference missing."
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
            # pyrefly: ignore [bad-argument-type]
            transaction_id=transaction_id
        )

        if validation_result.status == PaymentValidationResult.Status.SUCCESS:
            with transaction.atomic():
                if booking.room_id:
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
    if booking.room:
        booking.room.set_active_currency(booking.currency_code)
    elif booking.zipline_package:
        booking.zipline_package.set_active_currency(booking.currency_code)

    payments = Payment.objects.filter(booking=booking, status='success')
    
    context = {
        'booking': booking,
        'payments': payments,
        'print_date': timezone.now(),
    }
    return render(request, 'admin_dashboard/bookings/invoice.html', context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handles Stripe webhooks (checkout.session.completed, payment_intent.succeeded, payment_intent.payment_failed).
    Verifies signature if STRIPE_WEBHOOK_SECRET is set in environment.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    event = None
    if webhook_secret and sig_header:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error(f"Invalid Stripe webhook payload: {e}")
            return HttpResponse("Invalid payload", status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe webhook signature: {e}")
            return HttpResponse("Invalid signature", status=400)
    else:
        try:
            event_dict = json.loads(payload.decode('utf-8'))
            event = stripe.Event.construct_from(event_dict, stripe.api_key)
        except Exception as e:
            logger.error(f"Error parsing Stripe webhook JSON payload: {e}")
            return HttpResponse("Invalid JSON", status=400)

    try:
        # pyrefly: ignore [missing-attribute]
        event_type = event.type if hasattr(event, 'type') else event.get('type')
        # pyrefly: ignore [missing-attribute]
        event_data = event.data if hasattr(event, 'data') else event.get('data')

        logger.info(f"Received Stripe Webhook event: {event_type}")

        if event_type == 'checkout.session.completed':
            session = event_data.object if hasattr(event_data, 'object') else (event_data.get('object', {}) if isinstance(event_data, dict) else {})
            session_dict = session.to_dict() if hasattr(session, 'to_dict') else (dict(session) if isinstance(session, dict) else {})
            metadata = session_dict.get('metadata') or {}
            
            booking_uid = metadata.get('booking_uid')
            payment_id = metadata.get('payment_id')
            transaction_id = session_dict.get('client_reference_id') or metadata.get('transaction_id')

            payment = None
            if payment_id and str(payment_id).isdigit():
                payment = Payment.objects.filter(id=int(payment_id)).first()
            if not payment and transaction_id:
                payment = Payment.objects.filter(transaction_id=str(transaction_id)).first()
            if not payment and booking_uid:
                payment = Payment.objects.filter(booking__booking_uid=booking_uid, gateway='stripe').last()

            if payment and payment.status != 'success':
                booking = payment.booking
                with transaction.atomic():
                    if booking.room_id:
                        from rooms.models.room import Room
                        Room.objects.select_for_update().get(pk=booking.room_id)

                    if booking.has_room_availability():
                        payment.status = 'success'
                        try:
                            payment.gateway_response = json.dumps(session_dict, default=str)
                        except Exception:
                            payment.gateway_response = str(session_dict)
                        payment.save(update_fields=['status', 'gateway_response'])

                        booking.status = 'confirmed'
                        booking.save(update_fields=['status'])
                        logger.info(f"Booking {booking.booking_uid} successfully confirmed via Stripe Webhook.")
                    else:
                        payment.status = 'failed'
                        payment.gateway_response = 'Room inventory unavailable at webhook confirmation.'
                        payment.save(update_fields=['status', 'gateway_response'])
                        logger.warning(f"Booking {booking.booking_uid} failed availability check on Stripe Webhook.")

        elif event_type == 'payment_intent.payment_failed':
            pi = event_data.object if hasattr(event_data, 'object') else (event_data.get('object', {}) if isinstance(event_data, dict) else {})
            pi_dict = pi.to_dict() if hasattr(pi, 'to_dict') else (dict(pi) if isinstance(pi, dict) else {})
            metadata = pi_dict.get('metadata') or {}
            booking_uid = metadata.get('booking_uid')
            if booking_uid:
                payment = Payment.objects.filter(booking__booking_uid=booking_uid, gateway='stripe').last()
                if payment:
                    payment.status = 'failed'
                    payment.save(update_fields=['status'])

        return HttpResponse(status=200)

    except Exception as exc:
        # pyrefly: ignore [unbound-name]
        logger.exception(f"Error handling Stripe webhook event ({event_type}): {exc}")
        return HttpResponse(f"Webhook processing error: {exc}", status=500)

