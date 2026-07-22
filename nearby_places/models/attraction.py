from django.db import models
from core.utils import UploadTo, ValidateFileSize

class Attraction(models.Model):
    CATEGORY_CHOICES = [
        ('airport', 'Airport'),
        ('park', 'National Park / Wildlife Safari'),
        ('religious', 'Religious / Heritage Site'),
        ('tourist', 'Tourist Attraction'),
        ('border', 'Border Point'),
        ('city', 'Nearby City / Town'),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='tourist')
    distance = models.CharField(max_length=50, help_text="e.g. 15 km or 500 meters")
    travel_time = models.CharField(max_length=100, help_text="e.g. 20 minutes drive or 5 minutes walk")
    maps_url = models.URLField(blank=True, null=True, help_text="Google Maps direction link")
    image = models.ImageField(
        upload_to=UploadTo('attractions'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    description = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} ({self.distance})"
