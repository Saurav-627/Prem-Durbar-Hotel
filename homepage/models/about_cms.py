from django.db import models
from core.utils import UploadTo, ValidateFileSize

class AboutCMS(models.Model):
    hero_subtitle = models.CharField(max_length=150, default="Heritage & Mountain Hospitality")
    hero_title = models.CharField(max_length=150, default="Our Story & Legacy")
    hero_description = models.TextField(default="Nestled in Changunarayan-7, Nagarkot, Prem Durbar blends authentic Newari brick & wood craftsmanship with mountain tranquility, organic gastronomy, and high-altitude adventure.")
    hero_image = models.ImageField(upload_to=UploadTo('about/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])

    story_subtitle = models.CharField(max_length=150, default="Kathmandu Valley Artistry")
    story_title = models.CharField(max_length=200, default="Traditional Newari Architecture Meets Mountain Luxury")
    story_content = models.TextField(default="Prem Durbar was envisioned as a living tribute to Nepal's rich architectural heritage. Every brick, carved wood wooden struts, and terracotta tile was handcrafted by local artisans from Bhaktapur and Kathmandu Valley. Overlooking the serene Kamal Pokhari pond and pine forest ridge, our resort offers guests an immersive journey into Nepalese royal durbar elegance combined with modern five-star comfort.")
    story_extra = models.TextField(default="Overlooking the peaceful Kamal Pokhari (Lotus Pond) and surrounded by Nagarkot’s lush pine forests, our resort offers guests a tranquil retreat from urban life while keeping you connected to organic nature and panoramic Himalayan vistas.", blank=True)
    
    badge1_title = models.CharField(max_length=100, default="Handcrafted Decor")
    badge1_desc = models.CharField(max_length=200, default="Reclaimed wood beds & carved Newari window art.")
    badge2_title = models.CharField(max_length=100, default="Himalayan Panorama")
    badge2_desc = models.CharField(max_length=200, default="Unobstructed sunrise & sunset mountain views.")

    story_image1 = models.ImageField(upload_to=UploadTo('about/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])
    story_image2 = models.ImageField(upload_to=UploadTo('about/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])
    story_image3 = models.ImageField(upload_to=UploadTo('about/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])
    story_image4 = models.ImageField(upload_to=UploadTo('about/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo video URL for resort tour")

    zipline_callout_title = models.CharField(max_length=200, default="Nagarkot Zipline — The Superman Zip Line")
    zipline_callout_desc = models.TextField(default="Prem Durbar is proud home to Nepal’s longest, safest, and most thrill-inducing Superman Zipline. Soar through Nagarkot’s pine-clad hills with breathtaking views of Mount Everest and the Himalayan range.")
    zipline_callout_link_text = models.CharField(max_length=100, default="Explore Zipline Flight")

    team_subtitle = models.CharField(max_length=150, default="Passionate Hospitality Professionals")
    team_title = models.CharField(max_length=200, default="Meet Our Executive Leadership")

    class Meta:
        verbose_name = "About Page Content CMS"
        verbose_name_plural = "About Page Content CMS"

    def __str__(self):
        return "About Page Content CMS Settings"

    def save(self, *args, **kwargs):
        if not self.pk and AboutCMS.objects.exists():
            self.pk = AboutCMS.objects.first().pk
        super().save(*args, **kwargs)
