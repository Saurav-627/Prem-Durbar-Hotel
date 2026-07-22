from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from core.utils import UploadTo, ValidateFileSize

class GalleryItem(models.Model):
    category = models.ForeignKey('GalleryCategory', on_delete=models.CASCADE, related_name='items')
    image = models.ImageField(
        upload_to=UploadTo('gallery'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    caption = models.CharField(max_length=200, blank=True)
    
    is_video = models.BooleanField(default=False)
    is_drone = models.BooleanField(default=False)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube, Vimeo, or direct video URL")
    virtual_tour_url = models.URLField(blank=True, null=True, help_text="Virtual tour embed link")
    is_published = models.BooleanField(default=True, help_text="Designates whether this gallery item is visible on the website")

    created_at = models.DateTimeField(auto_now_add=True)

    # Fast responsive grid optimized image
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(600, 450)],
        format='JPEG',
        options={'quality': 80}
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"

    def __str__(self):
        item_type = "Video" if self.is_video else "Photo"
        return f"{self.category.name} - {self.caption or item_type} ({self.id})"
