from django.db import models
from django.utils.text import slugify
from core.utils import UploadTo, ValidateFileSize
from settings_manager.models.currency import Currency


class ZiplinePackage(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    highlights = models.TextField(blank=True, help_text="Comma or line separated highlights of this package")
    flight_type = models.CharField(max_length=100, default="Superman Flight", help_text="e.g. Superman, Tandem Dual, Classic Harness")
    duration = models.CharField(max_length=100, default="2 Minutes / 1.2 KM", help_text="Duration or distance specs")
    image = models.ImageField(
        upload_to=UploadTo('zipline/packages'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    image_url = models.URLField(blank=True, null=True, help_text="Fallback external image URL")
    is_featured = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Zipline Package"
        verbose_name_plural = "Zipline Packages"

    def __str__(self):
        base_price_val = self.base_price
        curr_code = self.currency.iso_code if self.currency else 'N/A'
        return f"{self.name} ({curr_code} {base_price_val}/person)"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while ZiplinePackage.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def set_active_currency(self, currency_code='USD'):
        self._active_currency_code = currency_code
        if hasattr(self, 'active_currency_price') and self.active_currency_price:
            matches = [p for p in self.active_currency_price if p.currency.iso_code == currency_code]
            self._active_price = matches[0] if matches else None
        else:
            self._active_price = self.base_prices.filter(currency__iso_code=currency_code).first()

    @property
    def base_price(self):
        active_price = getattr(self, '_active_price', None)
        if active_price and active_price.base_price:
            return active_price.base_price
        first_price = self.base_prices.first()
        return first_price.base_price if first_price else None

    @property
    def discount_price(self):
        active_price = getattr(self, '_active_price', None)
        if active_price and active_price.discount_price:
            return active_price.discount_price
        first_price = self.base_prices.first()
        return first_price.discount_price if first_price else None

    @property
    def currency(self):
        active_price = getattr(self, '_active_price', None)
        if active_price and active_price.currency:
            return active_price.currency
        first_price = self.base_prices.first()
        return first_price.currency if first_price else None

    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        return self.base_price or 0

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1533587851505-d119e13fa0d7?q=80&w=800'

    @property
    def added_base_prices(self):
        """Returns base prices greater than 0."""
        return [p for p in self.base_prices.all() if p.base_price and p.base_price > 0]


class ZiplinePackageBasePrice(models.Model):
    """Base price for a zipline package in a specific currency."""
    package = models.ForeignKey(
        ZiplinePackage,
        on_delete=models.CASCADE,
        related_name='base_prices'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='zipline_package_base_prices'
    )
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ('package', 'currency')
        verbose_name = "Zipline Package Base Price"
        verbose_name_plural = "Zipline Package Base Prices"

    def __str__(self):
        return f"{self.package.name} ({self.currency.iso_code}): {self.base_price}"
