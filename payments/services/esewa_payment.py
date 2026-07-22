import base64
import hashlib
import hmac
import logging

import requests
from requests.exceptions import HTTPError, JSONDecodeError

from .base_payment import BasePayment, PaymentValidationResult

logger = logging.getLogger(__name__)


class EsewaPayment(BasePayment):
    def generate_message_signature(self, message: str) -> str:
        hmac_sha256 = hmac.new(self.client_secret.encode(), message.encode(), hashlib.sha256)
        digest = hmac_sha256.digest()
        signature = base64.b64encode(digest).decode("utf-8")

        return signature

    def initiate_payment(self, *, total_amount: float, transaction_id: str, return_url: str, **kwargs) -> dict:
        message = f"total_amount={total_amount},transaction_uuid={transaction_id},product_code={self.client_id}"
        message_signature = self.generate_message_signature(message)
        tax_amount = kwargs.get('tax_amount', 0)

        if self.demo:
            url = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
        else:
            url = "https://epay.esewa.com.np/api/epay/main/v2/form"

        return {
            "api_url": url,
            "form_method": "POST",
            "provider_reference": None,
            "form_data": {
                "amount": str(total_amount - tax_amount),
                "tax_amount": str(float(tax_amount)),
                "total_amount": str(total_amount),
                "transaction_uuid": transaction_id,
                "product_code": self.client_id,
                "product_service_charge": str(0),
                "product_delivery_charge": str(0),
                "signed_field_names": "total_amount,transaction_uuid,product_code",
                "signature": message_signature,
                "success_url": return_url,
                "failure_url": return_url,
            },
        }

    def validate_payment(self, *, total_amount: float, transaction_id: str, request_timeout: int = 60, **kwargs) -> PaymentValidationResult:
        if self.demo:
            url = "https://rc.esewa.com.np/api/epay/transaction/status/"
        else:
            url = "https://esewa.com.np/api/epay/transaction/status/"

        response = requests.get(
            f"{url}?product_code={self.client_id}&total_amount={total_amount}&transaction_uuid={transaction_id}",
            headers={
                "Accept": "application/json",
            },
            timeout=request_timeout,
        )

        try:
            response.raise_for_status()
            epay_txn = response.json()
            # epay_txn----- {'product_code': 'EPAYTEST', 'transaction_uuid': '62635241-fb6e-4619-9147-bced63476f86', 'total_amount': 499.0, 'status': 'NOT_FOUND', 'ref_id': None}
            # epay_txn----- {'product_code': 'EPAYTEST', 'transaction_uuid': 'fcb2becb-6af4-4a28-8d5e-bb4cdaaef8c6', 'total_amount': 499.0, 'status': 'COMPLETE', 'ref_id': '000E99F'}
            # epay_txn----- {'product_code': 'EPAYTEST', 'transaction_uuid': 'fcb2becb-6af4-4a28-8d5e-bb4cdaaef8c6', 'total_amount': 499.0, 'status': 'PENDING', 'ref_id': '000E99F'}

            status = epay_txn.get("status")
            if status == "COMPLETE":
                return PaymentValidationResult(status=PaymentValidationResult.Status.SUCCESS)
            if status == "PENDING":
                return PaymentValidationResult(status=PaymentValidationResult.Status.PENDING)

            assert status in ["COMPLETE", "PENDING"], "Payment is not complete"

        except (HTTPError, JSONDecodeError, AssertionError, KeyError) as e:
            logger.error("-- eSewa cannot validate payment with reference %s %s" % (transaction_id, e))
            return PaymentValidationResult(status=PaymentValidationResult.Status.FAILED)
