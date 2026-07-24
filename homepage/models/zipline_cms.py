from django.db import models
from core.utils import UploadTo, ValidateFileSize

class ZiplineCMS(models.Model):
    hero_subtitle = models.CharField(max_length=150, default="Nagarkot Adventure Destination")
    hero_title = models.CharField(max_length=150, default="Nagarkot Zipline: The Superman Zip Line")
    hero_description = models.TextField(default="Soar through the skies of Nagarkot above lush pine forests with panoramic views of the Himalayan range and Mount Everest.")
    hero_image = models.ImageField(upload_to=UploadTo('zipline/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])

    # Video Preview (YouTube/Vimeo or uploaded MP4)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube, Vimeo, or external MP4 URL for Zipline video preview")
    video_file = models.FileField(upload_to=UploadTo('zipline/videos'), blank=True, null=True, help_text="Upload MP4 video file to play on the Zipline page")

    spec_length = models.CharField(max_length=50, default="1,200 Meters")
    spec_length_label = models.CharField(max_length=50, default="Flight Length")

    spec_speed = models.CharField(max_length=50, default="95 KM/H")
    spec_speed_label = models.CharField(max_length=50, default="Top Speed")

    spec_elevation = models.CharField(max_length=50, default="2,175m Altitude")
    spec_elevation_label = models.CharField(max_length=50, default="Altitude Elevation")

    spec_safety = models.CharField(max_length=50, default="100% International Certified")
    spec_safety_label = models.CharField(max_length=50, default="Safety Standard")

    booking_url = models.URLField(default="https://www.facebook.com/ziplinenagarkot", help_text="External URL for booking zipline (e.g. Facebook page or booking engine)")
    booking_button_text = models.CharField(max_length=100, default="Book Zipline Flight / Facebook Page")

    overview_subtitle = models.CharField(max_length=150, default="High-Altitude Thrill")
    overview_title = models.CharField(max_length=200, default="Nepal's Longest Superman Flight Zipline")
    overview_content = models.TextField(default="Located just 32 kilometers from Kathmandu at Changunarayan-7, Nagarkot, Nagarkot Zipline offers one of South Asia's most thrilling high-altitude zipline experiences. Choose between Superman Flight position, Tandem dual flight, or Classic harness zip as you glide above pine forests facing snow-capped peaks.")
    overview_image = models.ImageField(upload_to=UploadTo('zipline/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])
    image_caption_title = models.CharField(max_length=100, default="Superman Flying Harness")
    image_caption_subtitle = models.CharField(max_length=150, default="Head-first aerial view of Everest range")

    class Meta:
        verbose_name = "Zipline Page Content CMS"
        verbose_name_plural = "Zipline Page Content CMS"

    def __str__(self):
        return "Zipline Page Content CMS Settings"

    def save(self, *args, **kwargs):
        if not self.pk and ZiplineCMS.objects.exists():
            self.pk = ZiplineCMS.objects.first().pk
        super().save(*args, **kwargs)
