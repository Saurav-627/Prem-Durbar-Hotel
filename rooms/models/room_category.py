from django.db import models
from django.utils.text import slugify


class RoomCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Category display name, e.g. 'Deluxe Room'")
    slug = models.SlugField(max_length=120, unique=True, blank=True, help_text="Auto-generated URL-safe key, e.g. 'deluxe'")
    total_rooms = models.PositiveIntegerField(default=1, help_text="Total physical rooms available for this category across all currencies")
    order = models.IntegerField(default=0, help_text="Display order in dropdowns and filters")
    is_published = models.BooleanField(default=True, help_text="Show this category in room filters and admin dropdowns")

    class Meta:
        verbose_name = "Room Category"
        verbose_name_plural = "Room Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
