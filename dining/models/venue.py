from django.db import models
from django.utils.text import slugify
from core.utils import UploadTo, ValidateFileSize

class DiningVenue(models.Model):
    CATEGORY_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('bar', 'Bar'),
        ('cafe', 'Cafe'),
        ('lounge', 'Lounge'),
        ('private', 'Private Dining'),
        ('banquet', 'Banquet Menu'),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='restaurant')
    description = models.TextField()
    timings = models.CharField(max_length=100, help_text="e.g. 7:00 AM - 11:00 PM")
    menu_pdf = models.FileField(upload_to='dining/menus/', blank=True, null=True)
    
    # Chef Details
    chef_name = models.CharField(max_length=100, blank=True, null=True)
    chef_bio = models.TextField(blank=True, null=True)
    chef_image = models.ImageField(
        upload_to=UploadTo('dining/chefs'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    
    capacity = models.IntegerField(help_text="Guest capacity")
    featured_dishes = models.TextField(blank=True, help_text="Comma-separated list of featured dishes")
    video_url = models.URLField(blank=True, null=True, help_text="Virtual tour or venue intro video")
    image = models.ImageField(
        upload_to=UploadTo('dining/venues'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True, help_text="Designates whether this dining venue is visible on the website")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
