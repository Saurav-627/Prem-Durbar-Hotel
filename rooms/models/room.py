from django.db import models
from django.utils.text import slugify

class Room(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.ForeignKey(
        'RoomCategory',
        on_delete=models.PROTECT,
        related_name='rooms',
        help_text="Room category (managed in admin under Room Categories)"
    )
    description = models.TextField()
    highlights = models.TextField(help_text="Comma-separated or line-separated list of room highlights")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=None, help_text="Optional tax percentage for this room listing")
    room_size = models.IntegerField(help_text="Size in sq. ft. or sq. meters")
    max_adults = models.IntegerField(default=2)
    max_children = models.IntegerField(default=0)
    bed_type = models.CharField(max_length=100, default="King Size")
    facilities = models.ManyToManyField('RoomFacility', related_name='rooms', blank=True)
    virtual_tour_url = models.URLField(blank=True, null=True, help_text="Link to 3D virtual tour")
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo embed link")
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True, help_text="Designates whether this room is visible on the website")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    def set_active_currency(self, currency_code):
        self._active_currency_code = currency_code
        if hasattr(self, 'active_currency_price') and self.active_currency_price:
            # Check if active_currency_price prefetch matches the active currency code
            matches = [p for p in self.active_currency_price if p.currency.iso_code == currency_code]
            self._active_price = matches[0] if matches else None
        else:
            self._active_price = self.base_prices.filter(currency__iso_code=currency_code).first()

    @property
    def base_price(self):
        active_price = getattr(self, '_active_price', None)
        if active_price:
            return active_price.base_price
        first_price = self.base_prices.first()
        return first_price.base_price if first_price else None

    @property
    def discount_price(self):
        active_price = getattr(self, '_active_price', None)
        if active_price:
            return active_price.discount_price
        first_price = self.base_prices.first()
        return first_price.discount_price if first_price else None

    @property
    def currency(self):
        active_price = getattr(self, '_active_price', None)
        if active_price:
            return active_price.currency
        first_price = self.base_prices.first()
        return first_price.currency if first_price else None

    def __str__(self):
        base_price_val = self.base_price
        curr_code = self.currency.iso_code if self.currency else 'N/A'
        return f"{self.title} ({curr_code} {base_price_val}/night)"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def active_seasonal(self):
        """Return the active RoomSeasonalPrice override for today matching the active currency, or None."""
        import datetime
        today = datetime.date.today()
        active_currency_code = getattr(self, '_active_currency_code', None)
        seasonal_qs = getattr(self, '_prefetched_objects_cache', {}).get('seasonal_prices', None)
        if seasonal_qs is None:
            seasonal_qs = list(self.seasonal_prices.filter(is_active=True).select_related('currency'))
        for sp in seasonal_qs:
            if sp.start_date <= today <= sp.end_date and sp.is_active:
                if sp.currency_id is None or (active_currency_code and sp.currency.iso_code == active_currency_code):
                    return sp
        return None

    @property
    def current_price(self):
        """Return today's effective price: seasonal override or base_price."""
        sp = self.active_seasonal
        return sp.price_override if sp else self.base_price

    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.base_price

    @property
    def price_with_tax(self):
        price = self.final_price
        tax_pct = self.tax_percentage or 0
        return price + (price * (tax_pct / 100))

    @property
    def total_rooms(self):
        return self.category.total_rooms if self.category else 0

    @property
    def adults_range(self):
        return range(1, max(1, self.max_adults) + 1)

    @property
    def children_range(self):
        return range(0, max(0, self.max_children) + 1)

