from django.db import models
from django.utils import timezone
from decimal import Decimal


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount (in selected currency)'),
    ]

    APPLICABLE_TYPES = [
        ('all', 'All Products (Rooms & Zipline)'),
        ('room', 'Room Stays Only'),
        ('zipline', 'Zipline Flights Only'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, help_text="Internal note about this coupon (not shown to guests)")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="For percentage: enter 10 for 10%. For fixed: enter the amount in the guest's currency.")
    applicable_to = models.CharField(
        max_length=20,
        choices=APPLICABLE_TYPES,
        default='all',
        help_text="Restrict this coupon to a specific product type"
    )
    # Redemption limits
    max_uses = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum number of times this coupon can be redeemed. Leave empty for unlimited."
    )
    use_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of times this coupon has been redeemed (auto-tracked)."
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def is_valid(self, order_amount=0, product_type=None, active_currency_code=None):
        """
        Validate this coupon against:
        - Active status
        - Date window (valid_from, valid_to)
        - Product type restriction
        - Currency-specific minimum spend
        - Redemption limit
        """
        now = timezone.now()

        if not self.is_active:
            return False, "This coupon code is inactive or disabled."

        if now < self.valid_from:
            return False, "This coupon is not yet active."

        if now > self.valid_to:
            return False, "This coupon code has expired."

        if self.max_uses is not None and self.use_count >= self.max_uses:
            return False, "This coupon has reached its maximum redemption limit."

        if product_type and self.applicable_to != 'all' and self.applicable_to != product_type:
            target = "Room Stays" if self.applicable_to == 'room' else "Zipline Flights"
            return False, f"This coupon is valid for {target} only."

        # Check currency-specific minimum spend
        if active_currency_code:
            min_spend_obj = self.min_spends.filter(currency__iso_code=active_currency_code).first()
            if min_spend_obj and Decimal(str(order_amount)) < min_spend_obj.min_spend:
                return False, (
                    f"Minimum spend of {active_currency_code} {min_spend_obj.min_spend} "
                    f"required to apply this coupon."
                )

        return True, "Coupon is valid"

    def calculate_discount(self, order_amount):
        if self.discount_type == 'percentage':
            return (self.discount_value / Decimal('100.0')) * Decimal(str(order_amount))
        else:
            return min(Decimal(str(self.discount_value)), Decimal(str(order_amount)))

    def redeem(self):
        """Increment use_count when a booking is confirmed."""
        Coupon.objects.filter(pk=self.pk).update(use_count=models.F('use_count') + 1)

    @property
    def is_expired(self):
        return timezone.now() > self.valid_to

    @property
    def remaining_uses(self):
        if self.max_uses is None:
            return None
        return max(0, self.max_uses - self.use_count)

    def __str__(self):
        val = f"{self.discount_value}%" if self.discount_type == 'percentage' else f"{self.discount_value}"
        return f"{self.code} ({val} Off - {self.get_applicable_to_display()})"


class CouponMinSpend(models.Model):
    """Per-currency minimum spend requirements for a coupon."""
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='min_spends'
    )
    currency = models.ForeignKey(
        'settings_manager.Currency',
        on_delete=models.CASCADE,
        related_name='coupon_min_spends'
    )
    min_spend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Minimum order value in this currency to apply the coupon"
    )

    class Meta:
        unique_together = ('coupon', 'currency')
        verbose_name = "Coupon Min Spend"
        verbose_name_plural = "Coupon Min Spends"

    def __str__(self):
        return f"{self.coupon.code} → Min {self.currency.iso_code} {self.min_spend}"
