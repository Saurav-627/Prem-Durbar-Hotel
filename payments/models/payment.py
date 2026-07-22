from django.db import models
from decimal import Decimal

class Payment(models.Model):
    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('esewa', 'eSewa'),
        ('khalti', 'Khalti'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    booking = models.ForeignKey('booking.Booking', on_delete=models.CASCADE, related_name='payments')
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    currency = models.ForeignKey('settings_manager.Currency', on_delete=models.PROTECT, related_name='payments', null=True, blank=True)
    transaction_id = models.CharField(max_length=150, unique=True, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    
    # Logs and details
    gateway_response = models.TextField(blank=True, null=True, help_text="Raw JSON response from payment gateway")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} for Booking {self.booking.id} (${self.amount})"

    @property
    def tax_per_room(self):
        rooms = getattr(self.booking, 'num_rooms', 1) or 1
        if rooms <= 1:
            return self.tax_amount
        return Decimal(self.tax_amount) / Decimal(rooms)

    @property
    def amount_ex_tax(self):
        return Decimal(self.amount) - Decimal(self.tax_amount)
