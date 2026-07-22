from django.db import models

class NavigationMenu(models.Model):
    POSITION_CHOICES = [
        ('header', 'Header Main Navigation'),
        ('footer_links', 'Footer Quick Links'),
        ('footer_services', 'Footer Our Services'),
        ('footer_ota', 'Footer OTA Partners'),
    ]

    name = models.CharField(max_length=50)
    url = models.CharField(max_length=200, help_text="e.g. /rooms/ or https://booking.com")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='header')
    order = models.IntegerField(default=0)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children')
    is_published = models.BooleanField(default=True, help_text="Designates whether this menu item is visible on the website")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Navigation Menu Item"
        verbose_name_plural = "Navigation Menu Items"

    def __str__(self):
        return f"{self.position.replace('_', ' ').capitalize()} - {self.name}"
