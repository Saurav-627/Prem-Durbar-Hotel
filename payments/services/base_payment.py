from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

@dataclass
class PaymentValidationResult:
    class Status(Enum):
        SUCCESS = "success"
        FAILED = "failed"
        PENDING = "pending"
        OTHER = "Other"

    status: Status
    message: str | None = None
    details: dict | None = None
    validation_code: str | None = None
    transaction_status: str | None = None

class BasePayment(ABC):
    client_id: str | None
    client_secret: str
    demo: bool = True

    def __init__(self, *, client_id: str | None, client_secret: str | None, demo: bool = True):
        self.client_id = client_id
        self.client_secret = client_secret
        self.demo = demo

    @abstractmethod
    def initiate_payment(self, *, total_amount: float, transaction_id: str, return_url: str, product_items: list[dict] | None = None, **kwargs) -> dict:
        pass

    @abstractmethod
    def validate_payment(self, *, total_amount: float, transaction_id: str, request_timeout: int = 60, **kwargs) -> PaymentValidationResult:
        pass
