from django.db import models
from core.utils import UploadTo, ValidateFileSize

class SustainabilityCMS(models.Model):
    hero_subtitle = models.CharField(max_length=150, default="Responsible Hospitality")
    hero_title = models.CharField(max_length=150, default="Eco-Sustainability & Local Empowerment")
    hero_description = models.TextField(default="Preserving Nagarkot’s natural pine beauty and supporting local mountain communities while providing luxurious guest comfort.")
    hero_image = models.ImageField(upload_to=UploadTo('sustainability/cms'), blank=True, null=True, validators=[ValidateFileSize(2)])

    intro_subtitle = models.CharField(max_length=150, default="Pillars of Action")
    intro_title = models.CharField(max_length=200, default="Our Environmental & Community Commitments")

    class Meta:
        verbose_name = "Sustainability Page Content CMS"
        verbose_name_plural = "Sustainability Page Content CMS"

    def __str__(self):
        return "Sustainability Page Content CMS Settings"

    def save(self, *args, **kwargs):
        if not self.pk and SustainabilityCMS.objects.exists():
            self.pk = SustainabilityCMS.objects.first().pk
        super().save(*args, **kwargs)


class SustainabilityPillar(models.Model):
    icon_class = models.CharField(max_length=50, default="fa-solid fa-solar-panel", help_text="FontAwesome icon, e.g. fa-solid fa-leaf")
    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Sustainability Pillar"
        verbose_name_plural = "Sustainability Pillars"

    def __str__(self):
        return self.title
