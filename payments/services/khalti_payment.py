import logging
from typing import Any, Dict, Tuple, Union
from urllib.parse import urljoin, urlparse

import requests
from requests.exceptions import HTTPError, JSONDecodeError

from .utils import to_minor_units
from .exceptions import ApplicationError
from .base_payment import BasePayment, PaymentValidationResult

logger = logging.getLogger(__name__)


class KhaltiPayment(BasePayment):
    def base_api_url(self):
        if self.demo:
            return "https://dev.khalti.com/api/v2/"

        return "https://khalti.com/api/v2/"

    def send_request(
            self, path: str, 
            payload: Dict[str, Any], 
            request_timeout: Union[int, float, Tuple[float, float]] = (3.05, 10.0),
            ) -> dict:
        epayment_api = urljoin(self.base_api_url(), path)

        headers = {
            "Authorization": f"Key {self.client_secret}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            epayment_api,
            json=payload,
            headers=headers,
            timeout=request_timeout,
        )

        try:
            response.raise_for_status()
            return response.json()
        except HTTPError:
            try:
                error = response.json()  # validation error
                raise ApplicationError("Request failed", extra=error)
            except JSONDecodeError:
                error = response.text  # other error
                raise ApplicationError(error, extra={"status_code": response.status_code})

    def initiate_payment(
        self,
        *,
        total_amount: float,
        transaction_id: str,
        return_url: str,
        display_name: str,
        product_items: list[dict] = None,
        customer_info: dict = None,
        **kwargs,
    ):
        if customer_info is None:
            customer_info = {}
        if product_items is None:
            product_items = []

        parsed_url = urlparse(return_url)
        website_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        tax_amount = kwargs.get("tax_amount", 0)

        payload = {
            "return_url": return_url,
            "website_url": website_url,
            "amount": str(int(total_amount * 100)),
            "purchase_order_id": transaction_id,
            "purchase_order_name": display_name,
        }

        customer_info = {
            k: v for (k, v) in customer_info.items() if v
        }  # filter out payload values that must not be included if empty.

        if "name" in customer_info:  # name field is required if customer_info is provided
            payload["customer_info"] = customer_info

            payload["amount_breakdown"] = [{
                "label": "Product Price",
                "amount": to_minor_units(total_amount - tax_amount)
                }]
            if tax_amount > 0:
                payload["amount_breakdown"].append({
                    "label": "Tax",
                    "amount": to_minor_units(tax_amount)
                    })

        if product_items:
            payload["product_details"] = product_items

        payment_info = self.send_request("epayment/initiate/", payload)

        return {
            "api_url": payment_info["payment_url"],
            "provider_reference": payment_info["pidx"],
            "form_method": "GET",
            "form_data": {
                "pidx": payment_info["pidx"],
            },
        }

    def validate_payment(
            self, 
            *, 
            total_amount: float, 
            transaction_id: str, 
            **kwargs) -> PaymentValidationResult:
        try:
            data = self.send_request("epayment/lookup/", {"pidx": transaction_id})
            status = data.get("status", "").upper()

            assert status in ["COMPLETED", "PENDING"], "Payment is not complete"
            assert data["total_amount"] == int(total_amount * 100), "Payment amount mismatched"

            if status == "COMPLETED":
                return PaymentValidationResult(status=PaymentValidationResult.Status.SUCCESS)

            if status == "PENDING":
                return PaymentValidationResult(status=PaymentValidationResult.Status.PENDING)

            return PaymentValidationResult(status=PaymentValidationResult.Status.FAILED)
        except (ApplicationError, AssertionError, KeyError):
            logger.error("Khalti cannot validate payment with reference %s" % transaction_id)
            return PaymentValidationResult(status=PaymentValidationResult.Status.FAILED)
