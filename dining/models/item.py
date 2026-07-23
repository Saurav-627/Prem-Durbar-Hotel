from django.db import models
from django.utils.text import slugify
from core.utils import UploadTo, ValidateFileSize
from settings_manager.models.currency import Currency

class DiningCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="e.g. fa-solid fa-utensils")
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Dining Category'
        verbose_name_plural = 'Dining Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DiningItem(models.Model):
    category = models.ForeignKey(DiningCategory, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Default base price in NPR")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True, related_name='dining_items_default')
    image = models.ImageField(
        upload_to=UploadTo('dining/items'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    image_url = models.URLField(blank=True, null=True, help_text="External image URL fallback")
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    is_chef_special = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Dining Item'
        verbose_name_plural = 'Dining Items'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while DiningItem.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.category.name})"

    def set_active_currency(self, currency_code='USD'):
        self._active_currency_code = currency_code
        if hasattr(self, 'active_currency_price') and self.active_currency_price:
            matches = [p for p in self.active_currency_price if p.currency.iso_code == currency_code]
            self._active_price = matches[0] if matches else None
        else:
            self._active_price = self.base_prices.filter(currency__iso_code=currency_code).first()

    @property
    def current_price(self):
        active_price = getattr(self, '_active_price', None)
        if active_price and active_price.base_price:
            return active_price.base_price
        first_price = self.base_prices.first()
        if first_price and first_price.base_price:
            return first_price.base_price
        
        # Fallback exchange conversion if no explicit currency base price is entered yet
        curr_code = getattr(self, '_active_currency_code', 'USD')
        npr_val = float(self.base_price)
        if curr_code == 'NPR':
            return npr_val
        elif curr_code == 'INR':
            return round(npr_val / 1.6, 2)
        elif curr_code == 'EUR':
            return round(npr_val / 145.0, 2)
        elif curr_code == 'GBP':
            return round(npr_val / 170.0, 2)
        else:
            return round(npr_val / 135.0, 2)

    @property
    def currency_rel(self):
        active_price = getattr(self, '_active_price', None)
        if active_price:
            return active_price.currency
        first_price = self.base_prices.first()
        if first_price:
            return first_price.currency
        return self.currency

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?q=80&w=600'

    @property
    def active_price_info(self):
        curr_code = getattr(self, '_active_currency_code', 'USD')
        val = float(self.current_price or 0.0)
        curr = self.currency_rel
        symbol = curr.symbol if curr else ('RS.' if curr_code == 'NPR' else '$')
        return {
            'code': curr_code,
            'symbol': symbol,
            'amount': val,
            'formatted': f"{symbol} {val:,.2f}" if curr_code != 'NPR' else f"RS. {val:,.0f}"
        }


class DiningItemBasePrice(models.Model):
    """Permanent base price for a dining menu item in a specific currency."""
    item = models.ForeignKey(
        DiningItem,
        on_delete=models.CASCADE,
        related_name='base_prices'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name='dining_item_base_prices'
    )
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('item', 'currency')
        verbose_name = "Dining Item Base Price"
        verbose_name_plural = "Dining Item Base Prices"

    def __str__(self):
        return f"{self.item.title} ({self.currency.iso_code}): {self.base_price}"
