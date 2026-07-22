from django.db import models
from core.utils import UploadTo, ValidateFileSize

class SEOData(models.Model):
    path = models.CharField(max_length=255, unique=True, help_text="Relative path, e.g. '/' or '/rooms/' or '/contact/'")
    meta_title = models.CharField(max_length=80)
    meta_description = models.TextField(max_length=160)
    canonical_url = models.URLField(blank=True, null=True, help_text="Leave blank to use current page URL")

    # Header Banner Fields
    header_subtitle = models.CharField(max_length=150, blank=True, null=True, help_text="Subtitle shown in the page header banner")
    header_title = models.CharField(max_length=150, blank=True, null=True, help_text="Main title shown in the page header banner")
    header_description = models.TextField(blank=True, null=True, help_text="Description text shown in the page header banner")
    header_image = models.ImageField(
        upload_to=UploadTo('headers'),
        blank=True,
        null=True,
        help_text="Background image for the page banner",
        validators=[ValidateFileSize(2)]
    )

    # OG Tags
    og_title = models.CharField(max_length=80, blank=True, null=True)
    og_description = models.TextField(max_length=160, blank=True, null=True)
    og_image = models.ImageField(
        upload_to=UploadTo('seo'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )
    
    # Twitter Card
    twitter_card = models.CharField(max_length=20, default='summary_large_image', choices=[
        ('summary', 'Summary'),
        ('summary_large_image', 'Summary with Large Image'),
    ])

    # Structured Data (JSON-LD)
    structured_data = models.TextField(blank=True, null=True, help_text="Raw JSON-LD for schema markup")

    class Meta:
        verbose_name = "SEO Page Data"
        verbose_name_plural = "SEO Page Data"

    def __str__(self):
        return f"SEO: {self.path}"
