from django.db import models

class RoomFacility(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon_class = models.CharField(max_length=100, blank=True, null=True, help_text="FontAwesome or Lucide icon class")
    svg_path = models.TextField(blank=True, null=True, help_text="Raw SVG path data or SVG code for rendering custom icons")
    is_featured = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Room Facility"
        verbose_name_plural = "Room Facilities"

    def __str__(self):
        return self.name
