import logging

import stripe
from django.conf import settings

from .base_payment import BasePayment, PaymentValidationResult

logger = logging.getLogger(__name__)

class StripePayment(BasePayment):
    def __init__(self, *, client_id: str | None = None, client_secret: str | None = None, demo: bool = True):
        super().__init__(client_id=client_id, client_secret=client_secret or settings.STRIPE_SECRET_KEY, demo=demo)
        stripe.api_key = self.client_secret or settings.STRIPE_SECRET_KEY

    def initiate_payment(
        self,
        *,
        total_amount: float,
        transaction_id: str,
        return_url: str,
        product_items: list[dict] | None = None,
        **kwargs
    ) -> dict:
        stripe.api_key = self.client_secret or settings.STRIPE_SECRET_KEY
        
        currency = kwargs.get('currency', 'usd').lower()
        display_name = kwargs.get('display_name', 'Prem Durbar Hotel & Zipline Booking')
        customer_info = kwargs.get('customer_info') or {}
        cancel_url = kwargs.get('cancel_url') or return_url

        # Amount in minor units (e.g. cents / paisa)
        # pyrefly: ignore [unnecessary-type-conversion]
        amount_in_minor_units = round(total_amount * 100)

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'product_data': {
                            'name': display_name,
                            'description': f"Booking Ref: {transaction_id}",
                        },
                        'unit_amount': amount_in_minor_units,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                # pyrefly: ignore [bad-argument-type]
                customer_email=customer_info.get('email') or None,
                client_reference_id=transaction_id,
                metadata={
                    'transaction_id': transaction_id,
                    'booking_uid': str(kwargs.get('booking_uid', '')),
                    'payment_id': str(kwargs.get('payment_id', '')),
                },
                success_url=return_url + ("&" if "?" in return_url else "?") + "session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
            )

            return {
                'api_url': checkout_session.url,
                'form_method': 'REDIRECT',
                'form_data': {},
                'session_id': checkout_session.id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe initiate_payment failed: {e}")
            raise ValueError(f"Stripe initiation failed: {e.user_message if hasattr(e, 'user_message') else str(e)}")

    def validate_payment(
        self,
        *,
        total_amount: float,
        transaction_id: str,
        request_timeout: int = 60,
        **kwargs
    ) -> PaymentValidationResult:
        stripe.api_key = self.client_secret or settings.STRIPE_SECRET_KEY
        session_id = kwargs.get('session_id')

        try:
            if session_id:
                session = stripe.checkout.Session.retrieve(session_id)
                # pyrefly: ignore [no-matching-overload]
                session_dict = session.to_dict() if hasattr(session, 'to_dict') else dict(session)
                if session.payment_status == 'paid':
                    return PaymentValidationResult(
                        status=PaymentValidationResult.Status.SUCCESS,
                        message="Stripe payment completed successfully",
                        details=session_dict
                    )
                elif session.payment_status == 'unpaid':
                    return PaymentValidationResult(
                        status=PaymentValidationResult.Status.PENDING,
                        message="Stripe payment is still pending",
                        details=session_dict
                    )
                else:
                    return PaymentValidationResult(
                        status=PaymentValidationResult.Status.FAILED,
                        message=f"Stripe payment status: {session.payment_status}",
                        details=session_dict
                    )

            # Fallback check by PaymentIntent if provided
            payment_intent_id = kwargs.get('payment_intent_id')
            if payment_intent_id:
                pi = stripe.PaymentIntent.retrieve(payment_intent_id)
                # pyrefly: ignore [no-matching-overload]
                pi_dict = pi.to_dict() if hasattr(pi, 'to_dict') else dict(pi)
                if pi.status == 'succeeded':
                    return PaymentValidationResult(
                        status=PaymentValidationResult.Status.SUCCESS,
                        message="Stripe PaymentIntent succeeded",
                        details=pi_dict
                    )
                else:
                    return PaymentValidationResult(
                        status=PaymentValidationResult.Status.FAILED,
                        message=f"Stripe PaymentIntent status: {pi.status}",
                        details=pi_dict
                    )

            return PaymentValidationResult(
                status=PaymentValidationResult.Status.FAILED,
                message="Missing session_id or payment_intent_id for Stripe validation"
            )

        except Exception as e:
            logger.error(f"Stripe validate_payment error: {e}")
            return PaymentValidationResult(
                status=PaymentValidationResult.Status.FAILED,
                message=str(e)
            )
