from django.db import models
from core.utils import UploadTo, ValidateFileSize

class AboutPreview(models.Model):
    title = models.CharField(max_length=150, default="About Our Resort")
    subtitle = models.CharField(max_length=250, default="A Haven of Luxury & Hospitality")
    content = models.TextField(help_text="Introductory text about the hotel")
    image = models.ImageField(
        upload_to=UploadTo('homepage/about'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    video_url = models.URLField(blank=True, null=True, help_text="Promo video YouTube/Vimeo link")

    # Statistics Counters
    stat1_value = models.CharField(max_length=10, default="120")
    stat1_label = models.CharField(max_length=50, default="Luxury Rooms")
    
    stat2_value = models.CharField(max_length=10, default="5")
    stat2_label = models.CharField(max_length=50, default="Star Rating")
    
    stat3_value = models.CharField(max_length=10, default="3")
    stat3_label = models.CharField(max_length=50, default="Elite Restaurants")
    
    stat4_value = models.CharField(max_length=10, default="15+")
    stat4_label = models.CharField(max_length=50, default="Awards Won")

    class Meta:
        verbose_name = "Homepage About Preview"
        verbose_name_plural = "Homepage About Preview"

    def __str__(self):
        return "Homepage About Preview Settings"

    def save(self, *args, **kwargs):
        if not self.pk and AboutPreview.objects.exists():
            self.pk = AboutPreview.objects.first().pk
        super().save(*args, **kwargs)
