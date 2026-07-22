from django.db import models
from django.utils import timezone

from decimal import Decimal

class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount ($)'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self, order_amount=0):
        now = timezone.now()
        if not self.is_active:
            return False
        if not (self.valid_from <= now <= self.valid_to):
            return False
        if order_amount < self.min_spend:
            return False
        return True

    def calculate_discount(self, order_amount):
        if not self.is_valid(order_amount):
            return Decimal('0.00')
        if self.discount_type == 'percentage':
            return (self.discount_value / 100) * order_amount
        else:
            return min(self.discount_value, order_amount)

    def __str__(self):
        val = f"{self.discount_value}%" if self.discount_type == 'percentage' else f"${self.discount_value}"
        return f"{self.code} ({val} Off)"
