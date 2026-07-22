from django.db import models
from django.utils.text import slugify

class GalleryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    is_published = models.BooleanField(default=True, help_text="Designates whether this gallery category is visible on the website")

    class Meta:
        verbose_name = "Gallery Category"
        verbose_name_plural = "Gallery Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
