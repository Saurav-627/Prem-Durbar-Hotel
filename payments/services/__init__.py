from typing import Literal, TypedDict
from django.conf import settings

from .base_payment import BasePayment
from .esewa_payment import EsewaPayment
from .khalti_payment import KhaltiPayment
from .stripe_payment import StripePayment
from .email_service import send_booking_invoice_email

class PaymentProcessorConfig(TypedDict):
    code: Literal["esewa", "khalti", "stripe"]
    client_id: str | None
    client_secret: str
    demo: bool

def get_payment_processor(config: PaymentProcessorConfig) -> BasePayment:
    if config["code"] == "esewa":
        return EsewaPayment(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            demo=config["demo"],
        )
    elif config["code"] == "khalti":
        return KhaltiPayment(
            client_id=config["client_id"] or "",
            client_secret=config["client_secret"],
            demo=config["demo"],
        )
    elif config["code"] == "stripe":
        return StripePayment(
            client_id=config["client_id"] or "",
            client_secret=config["client_secret"],
            demo=config["demo"],
        )
    else:
        raise ValueError("Invalid payment processor %s" % config["code"])

def get_processor_by_gateway_name(gateway_name: str) -> BasePayment:
    """
    Helper to instantiate payment processor using django settings.
    """
    if gateway_name == "esewa":
        return get_payment_processor({
            "code": "esewa",
            "client_id": settings.ESEWA_CLIENT_ID,
            "client_secret": settings.ESEWA_CLIENT_SECRET,
            "demo": settings.ESEWA_DEMO
        })
    elif gateway_name == "khalti":
        return get_payment_processor({
            "code": "khalti",
            "client_id": settings.KHALTI_CLIENT_ID,
            "client_secret": settings.KHALTI_CLIENT_SECRET,
            "demo": settings.KHALTI_DEMO
        })
    elif gateway_name == "stripe":
        return get_payment_processor({
            "code": "stripe",
            "client_id": getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
            "client_secret": getattr(settings, 'STRIPE_SECRET_KEY', ''),
            "demo": True
        })
    else:
        raise ValueError(f"Unsupported gateway: {gateway_name}")

__all__ = [
    "BasePayment",
    "EsewaPayment",
    "KhaltiPayment",
    "StripePayment",
    "get_payment_processor",
    "get_processor_by_gateway_name",
    "PaymentProcessorConfig"
]
