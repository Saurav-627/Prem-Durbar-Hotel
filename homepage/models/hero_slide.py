from django.db import models
from core.utils import UploadTo, ValidateFileSize

class HeroSlide(models.Model):
    ANIMATION_CHOICES = [
        ('fadeInDown', 'Fade In Down'),
        ('fadeInUp', 'Fade In Up'),
        ('zoomIn', 'Zoom In'),
        ('slideInLeft', 'Slide In Left'),
        ('slideInRight', 'Slide In Right'),
    ]

    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=250, blank=True, null=True)
    background_image = models.ImageField(
        upload_to=UploadTo('homepage/hero'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    background_video_url = models.URLField(blank=True, null=True, help_text="YouTube or direct MP4 link")
    overlay_opacity = models.DecimalField(max_digits=3, decimal_places=2, default=0.50, help_text="Dark overlay opacity (0.00 to 1.00)")
    
    # CTA Buttons
    cta_text = models.CharField(max_length=50, default="Discover More")
    cta_url = models.CharField(max_length=200, default="/rooms/")
    cta2_text = models.CharField(max_length=50, blank=True, null=True, default="Book Now")
    cta2_url = models.CharField(max_length=200, blank=True, null=True, default="/booking/")

    # Animations
    title_animation = models.CharField(max_length=50, choices=ANIMATION_CHOICES, default='fadeInDown')
    subtitle_animation = models.CharField(max_length=50, choices=ANIMATION_CHOICES, default='fadeInUp')

    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"

    def __str__(self):
        return self.title
