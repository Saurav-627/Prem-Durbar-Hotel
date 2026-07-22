from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from core.utils import UploadTo, ValidateFileSize

class RoomImage(models.Model):
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to=UploadTo('rooms/gallery'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True, help_text="Accessibility alt text for screen readers")
    
    # Generate thumbnail spec using django-imagekit for performance
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 300)],
        format='JPEG',
        options={'quality': 85}
    )

    class Meta:
        verbose_name = "Room Image"
        verbose_name_plural = "Room Images"

    def __str__(self):
        return f"Image for {self.room.title} (Primary: {self.is_primary})"
