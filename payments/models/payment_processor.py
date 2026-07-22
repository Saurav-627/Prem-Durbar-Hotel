from django.db import models
from settings_manager.models.base import BaseModel

class PaymentProcessorCurrency(models.Model):
    payment_processor = models.ForeignKey(
        'PaymentProcessor',
        on_delete=models.CASCADE,
        db_column='payment_processor_id',
        related_name='+',
    )
    currency = models.ForeignKey(
        'settings_manager.Currency',
        on_delete=models.PROTECT,
        db_column='currency_id',
        related_name='+',
    )

    class Meta:
        db_table = 'payments_paymentprocessor_payment_currencies'
        indexes = [models.Index(fields=['payment_processor', 'currency'])]

class PaymentProcessor(BaseModel):
    name = models.CharField(max_length=128)
    code = models.SlugField(unique=True)
    
    # Currencies the customer can pay in
    payment_currencies = models.ManyToManyField(
        'settings_manager.Currency',
        through='PaymentProcessorCurrency',
        related_name="supported_by_processors",
    )
    
    apply_tax = models.BooleanField(default=True, help_text="Designates whether tax is applied on bookings using this processor")
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

    def supports_currency(self, iso_code):
        return self.payment_currencies.filter(iso_code=iso_code).exists()

    class Meta:
        verbose_name = "Payment Processor"
        verbose_name_plural = "Payment Processors"
        indexes = [
            models.Index(fields=["is_published"]),
            models.Index(fields=["code"]),
            models.Index(fields=["is_published", "id"]),
        ]
