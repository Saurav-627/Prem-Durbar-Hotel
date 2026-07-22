from django.db import models

class RoomSeasonalPrice(models.Model):
    """Temporary seasonal price override for a room during a date range."""
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='seasonal_prices')
    currency = models.ForeignKey(
        'settings_manager.Currency',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='seasonal_price_overrides',
        help_text="Currency this price override applies to. Leave blank to apply to all currencies."
    )
    name = models.CharField(max_length=100, help_text="e.g. Christmas Season, Summer Special")
    start_date = models.DateField()
    end_date = models.DateField()
    price_override = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per night during this period")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Room Seasonal Price"
        verbose_name_plural = "Room Seasonal Prices"
        ordering = ['start_date']

    def __str__(self):
        currency_str = self.currency.iso_code if self.currency else "ALL"
        return f"{self.name} - {self.room.title}: {currency_str} {self.price_override} ({self.start_date} to {self.end_date})"
